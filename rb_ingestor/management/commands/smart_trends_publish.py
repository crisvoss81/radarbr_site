# rb_ingestor/management/commands/smart_trends_publish.py
"""
Comando inteligente para publicação de notícias baseado em análise de audiência
"""
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
from rb_ingestor.trending_analyzer import TrendingAnalyzer
from rb_ingestor.audience_analyzer import AudienceAnalyzer
from rb_ingestor.enhanced_trending_sources import EnhancedTrendingSources

# Funções auxiliares (mesmas do comando original)
_NO_STATUS_SENTINEL = object()

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
    help = "Gera artigos inteligentes baseados em análise de audiência e trending topics."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=5, help="Número de artigos a serem criados.")
        parser.add_argument("--debug", action="store_true", help="Mostra mais informações sobre o processo.")
        parser.add_argument("--force", action="store_true", help="Força a publicação mesmo que um tópico similar já exista.")
        parser.add_argument("--strategy", choices=["trending", "audience", "mixed"], default="mixed", 
                          help="Estratégia de seleção de tópicos.")
        parser.add_argument("--include-seasonal", action="store_true", help="Inclui tópicos sazonais.")

    def handle(self, *args, **opts):
        Noticia = apps.get_model("rb_noticias", "Noticia")
        Categoria = apps.get_model("rb_noticias", "Categoria")

        cat_fallback, _ = Categoria.objects.get_or_create(slug="geral", defaults={"nome": "Geral"})

        # Inicializar analisadores
        trending_analyzer = TrendingAnalyzer()
        audience_analyzer = AudienceAnalyzer()
        enhanced_sources = EnhancedTrendingSources()

        # Obter insights da audiência
        audience_insights = audience_analyzer.get_audience_insights()
        
        if opts["debug"]:
            self.stdout.write(self.style.NOTICE("=== INSIGHTS DA AUDIÊNCIA ==="))
            self.stdout.write(f"Top categorias: {audience_insights['top_categories']}")
            self.stdout.write(f"Palavras-chave trending: {audience_insights['trending_keywords']}")
            self.stdout.write(f"Melhores horários: {audience_insights['best_publishing_hours']}")
            for rec in audience_insights['recommendations']:
                self.stdout.write(f"Recomendação: {rec}")

        # Selecionar estratégia de busca
        terms = []
        
        if opts["strategy"] == "trending":
            terms = self._get_enhanced_trending_topics(enhanced_sources, opts["limit"])
        elif opts["strategy"] == "audience":
            terms = self._get_audience_optimized_topics(audience_analyzer, opts["limit"])
        else:  # mixed
            terms = self._get_mixed_strategy_topics(enhanced_sources, audience_analyzer, opts["limit"])

        # Adicionar tópicos sazonais se solicitado
        if opts["include_seasonal"]:
            seasonal_topics = trending_analyzer.get_seasonal_topics()
            terms.extend(seasonal_topics[:2])  # Adicionar até 2 tópicos sazonais

        # Remover duplicatas e limitar
        terms = list(dict.fromkeys(terms))[:opts["limit"]]

        if opts["debug"]:
            self.stdout.write(self.style.NOTICE(f"=== TÓPICOS SELECIONADOS ==="))
            for i, term in enumerate(terms, 1):
                prediction = audience_analyzer.predict_topic_success(term)
                self.stdout.write(f"{i}. {term} (Score: {prediction['success_score']:.1f})")

        if not terms:
            self.stdout.write(self.style.ERROR("Nenhum tópico encontrado."))
            return

        # Processar tópicos usando a mesma lógica do publish_topic
        created = 0
        
        for topic in terms:
            topic_clean = topic.strip()
            key = f"smart_trend:{topic_clean.lower()}:{day}"

            if not opts["force"] and Noticia.objects.filter(fonte_url=key).exists():
                if opts["debug"]: self.stdout.write(f"– Já existe hoje: {topic_clean}")
                continue
            
            # Verificar se já existe uma notícia com título similar hoje
            today = timezone.localdate()
            similar_exists = Noticia.objects.filter(
                titulo__icontains=topic_clean[:20],  # Primeiros 20 caracteres
                criado_em__date=today
            ).exists()
            
            if not opts["force"] and similar_exists:
                if opts["debug"]: self.stdout.write(f"– Tópico similar já existe hoje: {topic_clean}")
                continue
            
            try:
                # Usar análise de audiência para categorização
                prediction = audience_analyzer.predict_topic_success(topic_clean)
                
                # Escolher categoria baseada na análise
                if prediction["success_score"] > 6:
                    # Tópico de alto potencial - usar categoria de melhor performance
                    if audience_insights["top_categories"]:
                        cat = Categoria.objects.filter(nome=audience_insights["top_categories"][0]).first() or cat_fallback
                    else:
                        cat_slug = route_category_for_topic(topic_clean)
                        cat = Categoria.objects.filter(slug=cat_slug).first() or cat_fallback
                else:
                    # Tópico normal - usar categorização padrão
                    cat_slug = route_category_for_topic(topic_clean)
                    cat = Categoria.objects.filter(slug=cat_slug).first() or cat_fallback

                self.stdout.write(f"Gerando artigo para: {topic_clean}...")
                art = generate_article(topic_clean) or {}
                
                title = strip_tags((art.get("title") or topic_clean).strip())[:200]
                conteudo = f'<p class="dek">{strip_tags((art.get("dek") or "").strip())[:220]}</p>\n{(art.get("html") or "<p></p>").strip()}'

                kwargs = {
                    "titulo": title, 
                    "conteudo": conteudo, 
                    "publicado_em": timezone.now(), 
                    "fonte_url": key, 
                    "categoria": cat, 
                    "fonte_nome": "RadarBR Smart Trends", 
                    "imagem_alt": title
                }
                if published_value is not _NO_STATUS_SENTINEL: 
                    kwargs["status"] = published_value

                # Usar update_or_create para evitar duplicatas
                obj, created_obj = Noticia.objects.update_or_create(
                    fonte_url=key,
                    defaults=kwargs
                )

                # Buscar imagem (mesma lógica do comando original)
                self.stdout.write(f"Buscando imagem para: {topic_clean}...")
                
                image_url = None
                if find_image_for_news and image_cache:
                    cached_url = image_cache.get(title, cat.slug)
                    if cached_url:
                        image_url = cached_url
                        self.stdout.write(f"✓ Imagem encontrada no cache")
                    else:
                        image_url = find_image_for_news(title, conteudo, cat.slug)
                        if image_url:
                            image_cache.set(title, image_url, cat.slug, {
                                'source': 'smart_trends_publish',
                                'topic': topic_clean,
                                'category': cat.slug,
                                'success_score': prediction['success_score']
                            })
                            self.stdout.write(f"✓ Imagem encontrada via API")
                
                if not image_url:
                    img_info = pick_image(topic_clean)
                    if img_info and img_info.get("url"):
                        remote_url = img_info["url"]
                        secure_url = upload_remote_to_cloudinary(
                            remote_url,
                            public_id=None,
                            folder="radarbr/noticias",
                            tags=["radarbr", "noticia", "smart"],
                        )
                        image_url = secure_url or remote_url
                        obj.imagem_credito = img_info.get("credito", "")
                        obj.imagem_licenca = img_info.get("licenca", "")
                        obj.imagem_fonte_url = img_info.get("fonte_url", remote_url)
                        self.stdout.write(f"✓ Imagem encontrada via sistema antigo")
                
                if image_url:
                    obj.imagem = image_url
                    self.stdout.write(self.style.SUCCESS(f"✓ Imagem para: {topic_clean}"))
                else:
                    self.stdout.write(self.style.WARNING("⚠ Nenhuma imagem encontrada"))

                obj.slug = unique_slug(title)
                obj.save()
                
                if created_obj:
                    created += 1
                    self.stdout.write(self.style.SUCCESS(f"✓ Novo artigo criado: {topic_clean}"))
                else:
                    self.stdout.write(self.style.WARNING(f"⚠ Artigo já existia, atualizado: {topic_clean}"))
                
                # Mostrar predição de sucesso
                self.stdout.write(self.style.SUCCESS(f"✓ Publicado: {topic_clean} (Score: {prediction['success_score']:.1f})"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erro ao processar o tópico '{topic_clean}': {str(e)}"))
                if opts["debug"]: traceback.print_exc()
                continue

        self.stdout.write(self.style.SUCCESS(f"Pronto. Novos artigos criados: {created}"))

        # Ping sitemap (mesma lógica do comando original)
        if created > 0:
            try:
                from core.utils import absolute_sitemap_url
                from rb_ingestor.ping import ping_search_engines
                sm_url = absolute_sitemap_url()
                res = ping_search_engines(sm_url)
                self.stdout.write(self.style.NOTICE(f"Ping sitemap: Google={'OK' if res['google'] else 'NOK'}; Bing={'OK' if res['bing'] else 'NOK'}"))
            except Exception: pass

    def _get_trending_topics(self, analyzer: TrendingAnalyzer, limit: int) -> list:
        """Obtém tópicos baseados em trending topics"""
        topics = analyzer.get_optimized_topics(limit)
        return [topic["topic"] for topic in topics]

    def _get_audience_optimized_topics(self, analyzer: AudienceAnalyzer, limit: int) -> list:
        """Obtém tópicos otimizados para a audiência atual"""
        insights = analyzer.get_audience_insights()
        
        # Gerar tópicos baseados nas palavras-chave de alto engajamento
        topics = []
        for keyword in insights["trending_keywords"][:3]:
            # Gerar variações do tópico
            variations = [
                f"como {keyword}",
                f"melhor {keyword}",
                f"dicas sobre {keyword}",
                f"guia completo {keyword}"
            ]
            topics.extend(variations)
        
        return topics[:limit]

    def _get_mixed_strategy_topics(self, enhanced_sources: EnhancedTrendingSources, 
                                 audience_analyzer: AudienceAnalyzer, limit: int) -> list:
        """Combina estratégias de trending topics e análise de audiência"""
        # 60% trending topics, 40% audience optimized
        trending_count = int(limit * 0.6)
        audience_count = limit - trending_count
        
        trending_topics = self._get_enhanced_trending_topics(enhanced_sources, trending_count)
        audience_topics = self._get_audience_optimized_topics(audience_analyzer, audience_count)
        
        return trending_topics + audience_topics
    
    def _get_enhanced_trending_topics(self, enhanced_sources: EnhancedTrendingSources, limit: int) -> list:
        """Busca tópicos em ascensão usando fontes aprimoradas"""
        try:
            self.stdout.write("🔍 Buscando temas em ascensão de múltiplas fontes...")
            
            # Obter todos os trending topics
            trending_data = enhanced_sources.get_all_trending_topics(limit * 2)
            
            if not trending_data:
                self.stdout.write("⚠ Nenhum trending topic encontrado")
                return []
            
            # Extrair apenas os tópicos
            topics = []
            for item in trending_data[:limit]:
                topic = item.get('topic', '')
                if topic:
                    topics.append(topic)
                    if self.stdout.verbosity >= 1:
                        source = item.get('source', 'unknown')
                        score = item.get('trend_score', 0)
                        category = item.get('category', 'geral')
                        self.stdout.write(f"  📈 {topic} (Fonte: {source}, Score: {score}, Categoria: {category})")
            
            self.stdout.write(f"✅ Encontrados {len(topics)} temas em ascensão")
            return topics
            
        except Exception as e:
            self.stdout.write(f"❌ Erro ao buscar trending topics: {e}")
            return []
