# rb_ingestor/management/commands/trends_publish.py
import traceback
from django.core.management.base import BaseCommand
from django.apps import apps
from django.utils import timezone
from django.utils.html import strip_tags
from django.db import models
from slugify import slugify

from gnews import GNews
from rb_ingestor.ai import generate_article
from rb_ingestor.images_free import pick_image
from rb_ingestor.images_cloudinary import upload_remote_to_cloudinary
from rb_ingestor.categorize import route_category_for_topic
from rb_ingestor.image_search import find_image_for_news
from rb_ingestor.image_cache import image_cache

# (As funções auxiliares _status_published, etc. não precisam de alteração)
_NO_STATUS_SENTINEL = object()
# ... (código das funções auxiliares permanece o mesmo)
def _flatten_choices(choices):
    flat = []
    for c in choices or []:
        if isinstance(c, (list, tuple)) and len(c) == 2 and isinstance(c[1], (list, tuple)):
            flat.extend(c[1])
        else:
            flat.append(c)
    return flat
def _pick_published_from_choices(choices):
    keys = {"published", "publicado", "publicada", "ativo", "aprovado", "online"}
    for value, label in choices:
        v = str(value).lower(); l = str(label).lower()
        if v in keys or l in keys: return value
    return choices[0][0]
def _status_published(Noticia):
    try: f = Noticia._meta.get_field("status")
    except Exception: return _NO_STATUS_SENTINEL
    default = getattr(f, "default", models.fields.NOT_PROVIDED)
    if default is not models.fields.NOT_PROVIDED and default is not None and default != "": return default
    flat = _flatten_choices(getattr(f, "choices", None))
    if flat: return _pick_published_from_choices(flat)
    if isinstance(f, (models.IntegerField, models.SmallIntegerField, models.PositiveIntegerField, models.PositiveSmallIntegerField, models.BigIntegerField)): return 1
    return "published"


class Command(BaseCommand):
    help = "Gera artigos a partir de tópicos do Google News (BR) + imagem livre."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=5, help="Número de artigos a serem criados.")
        parser.add_argument("--debug", action="store_true", help="Mostra mais informações sobre o processo.")
        parser.add_argument("--force", action="store_true", help="Força a publicação mesmo que um tópico similar já exista.")
        parser.add_argument("--topics", nargs="+", help="Lista de tópicos manuais para usar em vez de buscar no Google News.")

    def handle(self, *args, **opts):
        Noticia = apps.get_model("rb_noticias", "Noticia")
        Categoria = apps.get_model("rb_noticias", "Categoria")

        cat_fallback, _ = Categoria.objects.get_or_create(slug="geral", defaults={"nome": "Geral"})

        # --- LÓGICA DE BUSCA MELHORADA COM DIAGNÓSTICO E FALLBACK ---
        terms = []
        
        # Se tópicos manuais foram fornecidos, usa eles
        if opts.get("topics"):
            terms = opts["topics"][:opts["limit"]]
            self.stdout.write(self.style.NOTICE(f"Usando tópicos manuais: {terms}"))
        else:
            self.stdout.write(self.style.NOTICE("Buscando tópicos no Google News..."))
            
            try:
                # Inicialização do GNews com configurações otimizadas
                google_news = GNews(
                    language='pt', 
                    country='BR', 
                    period='1d', 
                    max_results=opts["limit"] * 3,
                    exclude_websites=['youtube.com', 'instagram.com', 'facebook.com']  # Excluir redes sociais
                )
                
                if opts["debug"]:
                    self.stdout.write("DEBUG: GNews inicializado com sucesso")
                
                # 1. Tenta buscar "Top News"
                raw_articles = []
                try:
                    raw_articles = google_news.get_top_news()
                    if opts["debug"]:
                        self.stdout.write(f"DEBUG: GNews (Top News) retornou {len(raw_articles)} artigos.")
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Erro ao buscar Top News: {str(e)}"))
                    if opts["debug"]:
                        traceback.print_exc()

                # 2. Se falhar, tenta termos específicos como fallback
                if not raw_articles:
                    self.stdout.write(self.style.WARNING("Top News não retornou resultados. Tentando fallbacks..."))
                    
                    fallback_terms = [
                        'notícias do Brasil',
                        'política Brasil',
                        'economia Brasil',
                        'tecnologia Brasil',
                        'esportes Brasil'
                    ]
                    
                    for term in fallback_terms:
                        try:
                            raw_articles = google_news.get_news(term)
                            if raw_articles:
                                if opts["debug"]:
                                    self.stdout.write(f"DEBUG: Fallback '{term}' retornou {len(raw_articles)} artigos.")
                                break
                        except Exception as e:
                            if opts["debug"]:
                                self.stdout.write(f"DEBUG: Erro ao buscar '{term}': {str(e)}")
                            continue
                
                # 3. Processamento dos artigos encontrados
                if raw_articles:
                    seen_titles = set()
                    for article in raw_articles:
                        title = article.get('title', '').strip()
                        
                        # Limpa o título removendo fonte e caracteres especiais
                        if ' - ' in title:
                            title = title.rsplit(' - ', 1)[0].strip()
                        
                        # Remove caracteres especiais e normaliza
                        title = title.replace('|', '').replace('•', '').strip()
                        
                        if title and len(title) > 10 and title.lower() not in seen_titles:
                            seen_titles.add(title.lower())
                            terms.append(title)
                    
                    terms = terms[:opts["limit"]]
                    
                    if opts["debug"]:
                        self.stdout.write(f"DEBUG: Processados {len(terms)} tópicos únicos")
                else:
                    self.stdout.write(self.style.WARNING("Nenhum artigo encontrado em nenhum método de busca"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Falha crítica ao buscar notícias do GNews: {str(e)}"))
                if opts["debug"]:
                    traceback.print_exc()
        # --- FIM DA LÓGICA MELHORADA ---

        if opts["debug"]:
            self.stdout.write(self.style.NOTICE(f"Tópicos úteis encontrados ({len(terms)}): {terms}"))

        if not terms:
            self.stdout.write(self.style.ERROR("Nenhum tópico encontrado, mesmo após o fallback. Verifique a conexão do servidor ou o log de erros."))
            return

        created = 0
        day = timezone.localdate().isoformat()

        def unique_slug(base_title: str) -> str:
            base = (slugify(base_title) or "post")[:180]
            slug, i = base, 2
            while Noticia.objects.filter(slug=slug).exists():
                slug = f"{base[:176]}-{i}"; i += 1
            return slug

        published_value = _status_published(Noticia)
        
        for topic in terms:
            topic_clean = topic.strip()
            key = f"trend:{topic_clean.lower()}:{day}"

            if not opts["force"] and Noticia.objects.filter(fonte_url=key).exists():
                if opts["debug"]: self.stdout.write(f"– Já existe hoje: {topic_clean}")
                continue
            
            try:
                cat_slug = route_category_for_topic(topic_clean)
                cat = Categoria.objects.filter(slug=cat_slug).first() or cat_fallback

                self.stdout.write(f"Gerando artigo para: {topic_clean}...")
                art = generate_article(topic_clean) or {}
                
                title = strip_tags((art.get("title") or topic_clean).strip())[:200]
                conteudo = f'<p class="dek">{strip_tags((art.get("dek") or "").strip())[:220]}</p>\n{(art.get("html") or "<p></p>").strip()}'

                kwargs = {"titulo": title, "conteudo": conteudo, "publicado_em": timezone.now(), "fonte_url": key, "categoria": cat, "fonte_nome": "RadarBR via GNews", "imagem_alt": title}
                if published_value is not _NO_STATUS_SENTINEL: kwargs["status"] = published_value

                obj = Noticia(**kwargs)

                self.stdout.write(f"Buscando imagem para: {topic_clean}...")
                
                # Tentar novo sistema de busca de imagens primeiro
                image_url = None
                if find_image_for_news and image_cache:
                    # Verificar cache primeiro
                    cached_url = image_cache.get(title, cat_slug)
                    if cached_url:
                        image_url = cached_url
                        self.stdout.write(f"✓ Imagem encontrada no cache")
                    else:
                        # Buscar nova imagem
                        image_url = find_image_for_news(title, conteudo, cat_slug)
                        if image_url:
                            # Armazenar no cache
                            image_cache.set(title, image_url, cat_slug, {
                                'source': 'trends_publish',
                                'topic': topic_clean,
                                'category': cat_slug
                            })
                            self.stdout.write(f"✓ Imagem encontrada via API")
                
                # Fallback para sistema antigo se novo sistema não funcionar
                if not image_url:
                    img_info = pick_image(topic_clean)
                    if img_info and img_info.get("url"):
                        remote_url = img_info["url"]
                        # Tentar subir para Cloudinary; se falhar, manter a URL remota
                        secure_url = upload_remote_to_cloudinary(
                            remote_url,
                            public_id=None,
                            folder="radarbr/noticias",
                            tags=["radarbr", "noticia"],
                        )
                        image_url = secure_url or remote_url
                        obj.imagem_credito = img_info.get("credito", "")
                        obj.imagem_licenca = img_info.get("licenca", "")
                        obj.imagem_fonte_url = img_info.get("fonte_url", remote_url)
                        self.stdout.write(f"✓ Imagem encontrada via sistema antigo")
                
                if image_url:
                    obj.imagem = image_url
                    msg = "API" if find_image_for_news else "sistema antigo"
                    self.stdout.write(self.style.SUCCESS(f"✓ Imagem ({msg}) para: {topic_clean}"))
                else:
                    self.stdout.write(self.style.WARNING("⚠ Nenhuma imagem encontrada"))

                obj.slug = unique_slug(title)
                obj.save()
                created += 1
                self.stdout.write(self.style.SUCCESS(f"✓ Publicado: {topic_clean}"))

            except Exception:
                self.stdout.write(self.style.ERROR(f"Erro ao processar o tópico '{topic_clean}':"))
                if opts["debug"]: traceback.print_exc()
                continue

        self.stdout.write(self.style.SUCCESS(f"Pronto. Novos artigos criados: {created}"))

        if created > 0:
            try:
                from core.utils import absolute_sitemap_url
                from rb_ingestor.ping import ping_search_engines
                sm_url = absolute_sitemap_url()
                res = ping_search_engines(sm_url)
                self.stdout.write(self.style.NOTICE(f"Ping sitemap: Google={'OK' if res['google'] else 'NOK'}; Bing={'OK' if res['bing'] else 'NOK'}"))
            except Exception: pass