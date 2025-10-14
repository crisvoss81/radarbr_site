# rb_ingestor/management/commands/publish_topic_simple.py
"""
Comando SIMPLIFICADO para publicar artigo
Lógica direta: Buscar notícia → Gerar conteúdo → Publicar
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.html import strip_tags
from slugify import slugify
from django.apps import apps
import os
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Publica artigo de forma SIMPLES: busca notícia, gera conteúdo, publica"

    def add_arguments(self, parser):
        parser.add_argument("topic", type=str, help="Tópico para o artigo")
        parser.add_argument("--words", type=int, default=800, help="Número de palavras (padrão: 800)")
        parser.add_argument("--force", action="store_true", help="Força publicação")
        parser.add_argument("--news-url", type=str, default=None, help="URL direto do Google News para usar como base")

    def handle(self, *args, **options):
        topic = options["topic"]
        min_words = options["words"]
        
        self.stdout.write(f"=== PUBLICAÇÃO SIMPLES: {topic} ===")
        
        # 1. BUSCAR NOTÍCIA (ou usar URL fornecida)
        direct_url = options.get("--news_url") or options.get("news_url")
        if direct_url:
            news_article = {"title": "", "description": "", "link": direct_url}
            self.stdout.write(f"📰 Usando URL direta do Google News: {direct_url[:60]}...")
        else:
            # Nova extração: tentar até 3 itens do RSS abrindo no navegador (sem fallback gnews)
            try:
                from rb_ingestor.news_content_extractor import NewsContentExtractor
                extractor = NewsContentExtractor()
                best = extractor.extract_best_for_topic(topic, max_items=3)
                if best and best.get('url'):
                    news_article = {'title': best.get('title',''), 'description': best.get('description',''), 'link': best.get('url')}
                    self.stdout.write(f"📰 Notícia (RSS) encontrada: {news_article['title'][:60]}...")
                else:
                    self.stdout.write("❌ Nenhum item válido encontrado no RSS do Google News")
                    return
            except Exception as e:
                self.stdout.write(f"❌ Erro na extração via RSS/navegador: {e}")
                return
        
        # 2. GERAR TÍTULO
        title = self._generate_title(topic, news_article)
        
        # 3. GERAR CONTEÚDO
        content = self._generate_content(topic, news_article, min_words)
        
        # Se não conseguiu gerar conteúdo, cancelar
        if not content:
            self.stdout.write("❌ Falha na geração de conteúdo. Publicação cancelada.")
            return
        
        # 4. DETERMINAR CATEGORIA (prioriza categoria do publisher quando disponível)
        category = self._determine_category_with_publisher(topic, content, news_article)
        
        # 5. PUBLICAR
        self._publish_article(title, content, category, topic)
        
        self.stdout.write("✅ Artigo publicado com sucesso!")

    def _search_news(self, topic):
        """Busca notícia no Google News priorizando o link RSS (news.google.com/rss/articles/...)"""
        # 1) Tentar via RSS oficial do Google News para o termo pesquisado
        try:
            import requests
            import urllib.parse
            import xml.etree.ElementTree as ET

            q = urllib.parse.quote_plus(topic)
            rss_url = f"https://news.google.com/rss/search?q={q}&hl=pt-BR&gl=BR&ceid=BR:pt-BR"
            resp = requests.get(rss_url, timeout=15)
            if resp.status_code == 200 and resp.text.strip():
                root = ET.fromstring(resp.text)
                channel = root.find('channel')
                if channel is not None:
                    item = channel.find('item')
                    if item is not None:
                        title_el = item.find('title')
                        link_el = item.find('link')
                        desc_el = item.find('description')
                        article = {
                            'title': title_el.text if title_el is not None else '',
                            'link': link_el.text if link_el is not None else '',
                            'description': desc_el.text if desc_el is not None else ''
                        }
                        if article.get('link'):
                            self.stdout.write(f"📰 Notícia (RSS) encontrada: {article.get('title', 'Sem título')[:50]}...")
                            return article
        except Exception as e:
            self.stdout.write(f"⚠️ Falha busca RSS: {e}")

        # 2) Fallback: biblioteca gnews
        try:
            from gnews import GNews

            google_news = GNews()
            google_news.language = "pt"
            google_news.country = "BR"
            google_news.max_results = 1

            articles = google_news.get_news(topic)

            if articles:
                article = articles[0]
                self.stdout.write(f"📰 Notícia encontrada: {article.get('title', 'Sem título')[:50]}...")
                return article
            return None

        except Exception as e:
            self.stdout.write(f"❌ Erro ao buscar notícia (fallback): {e}")
            return None

    def _generate_title(self, topic, news_article):
        """Gera título único e humanizado baseado na notícia"""
        if news_article and news_article.get('title'):
            import re
            original_title = news_article['title']

            # 1) Remover marcas de portal conhecidas
            portals = [
                'G1', 'Globo', 'Folha', 'Estadão', 'UOL', 'Terra', 'R7', 'IG', 'Exame',
                'Metrópoles', 'CNN', 'BBC', 'Agência Brasil', 'InfoMoney', 'GZH',
                'CidadeVerde.com', 'Midiamax', 'CLAUDIA', 'O Globo', 'Rádio Itatiaia',
                'Band', 'Jornal Correio', 'TV Cultura'
            ]
            clean_title = original_title
            for portal in portals:
                clean_title = clean_title.replace(f' - {portal}', '').replace(f' | {portal}', '').replace(f' ({portal})', '')

            # 2) Remover prefixos de seção/coluna e nomes de colunistas (substituir por genérico)
            patterns_to_strip = [
                r'(?i)^opini[aã]o\s*[-:]+\s*',
                r'(?i)^coluna\s*[-:]+\s*',
                r'(?i)^an[áa]lise\s*[-:]+\s*',
                r'(?i)^blog\s*[-:]+\s*'
            ]
            for pat in patterns_to_strip:
                clean_title = re.sub(pat, '', clean_title).strip()

            # Substituir padrões "por NOME" por um genérico
            clean_title = re.sub(r'(?i)\bpor\s+[A-ZÁÂÃÉÊÍÓÔÕÚÜÇ][^\-|:]+', 'por especialistas', clean_title)
            # Se título iniciar com "Nome: ...", substituir o nome
            clean_title = re.sub(r'^(?:[A-ZÁÂÃÉÊÍÓÔÕÚÜÇ][a-záâãéêíóôõúüç]+\s+){1,3}:', 'Especialistas:', clean_title).strip()

            # 3) Normalizar espaços e remover duplicidades de pontuação
            clean_title = re.sub(r'\s+', ' ', clean_title)
            clean_title = re.sub(r'[:\-—]\s*$', '', clean_title).strip()

            # 4) Criar variações SEO/Humanizadas sem plagiar
            base = clean_title
            # Evitar repetir prefixos se já existirem no título base
            lowered = base.lower()
            candidate_variations = [
                f"O que muda com {base}",
                f"{base} — contexto e impactos",
                f"{base}: pontos-chave e próximos passos",
                f"{base} | o que aconteceu e o que vem aí",
                f"Análise: {base}",
                f"Resumo e próximos passos: {base}",
                f"{base}: entenda em detalhes",
                f"{base}: análise completa",
                f"{base}: o que você precisa saber",
                f"{base}: fatos e perspectivas",
            ]
            # Só usar "Entenda o caso" se não estiver no início do título final com frequência
            if not lowered.startswith("entenda o caso") and "entenda o caso" not in lowered:
                candidate_variations.append(f"Entenda o caso: {base}")

            # Seleção pseudo-determinística para variar (hash do título base)
            try:
                idx = (abs(hash(base)) % len(candidate_variations))
            except Exception:
                idx = 0
            # Tentar a partir do índice calculado, respeitando limite de 120 chars
            for offset in range(len(candidate_variations)):
                v = candidate_variations[(idx + offset) % len(candidate_variations)]
                if len(v) <= 120:
                    return v
            return candidate_variations[0][:120]
        
        return f"Análise completa: {topic.title()}"

    def _generate_content(self, topic, news_article, min_words):
        """Gera conteúdo baseado na notícia encontrada com margem de 15% da notícia base"""
        # Extrair conteúdo completo da notícia base
        base_word_count = self._extract_full_news_content(news_article)
        if base_word_count == 0:
            base_word_count = min_words
            self.stdout.write(f"⚠️ Não foi possível extrair conteúdo completo, usando {min_words} palavras")
        else:
            self.stdout.write(f"📊 Notícia base completa: {base_word_count} palavras")
        
        # Calcular margem de 15% baseada na notícia
        target_min = int(base_word_count * 0.85)
        target_max = int(base_word_count * 1.15)
        self.stdout.write(f"🎯 Margem 15%: {target_min}-{target_max} palavras")
        
        # Tentar IA (baseada na notícia) - primeira tentativa
        if self._has_openai_key():
            content = self._generate_with_ai_from_news(topic, news_article, target_min)
            if content:
                word_count = len(strip_tags(content).split())
                # Verificar margem de 15% baseada na notícia
                if target_min <= word_count <= target_max:
                    self.stdout.write(f"🤖 Conteúdo gerado por IA: {word_count} palavras (margem: 15%)")
                    return content
                elif word_count >= target_min * 0.9:  # Aceitar se estiver próximo (90% do mínimo)
                    self.stdout.write(f"🤖 Conteúdo gerado por IA: {word_count} palavras (aceito por estar próximo da margem)")
                    return content
                else:
                    self.stdout.write(f"⚠️ IA gerou {word_count} palavras (fora da margem de 15%)")
            
            # Segunda tentativa se a primeira falhou
            self.stdout.write("🔄 Tentando IA novamente...")
            content = self._generate_with_ai_from_news(topic, news_article, target_min)
            if content:
                word_count = len(strip_tags(content).split())
                if target_min <= word_count <= target_max:
                    self.stdout.write(f"🤖 Conteúdo gerado por IA (2ª tentativa): {word_count} palavras (margem: 15%)")
                    return content
                elif word_count >= target_min * 0.9:  # Aceitar se estiver próximo (90% do mínimo)
                    self.stdout.write(f"🤖 Conteúdo gerado por IA (2ª tentativa): {word_count} palavras (aceito por estar próximo da margem)")
                    return content
                else:
                    self.stdout.write(f"⚠️ IA (2ª tentativa) gerou {word_count} palavras (fora da margem de 15%)")
        
        # Se IA falhou duas vezes, cancelar publicação
        self.stdout.write("❌ IA falhou em ambas as tentativas. Cancelando publicação.")
        return None

    def _extract_full_news_content(self, news_article):
        """Extrai o conteúdo completo da notícia para contar palavras"""
        if not news_article:
            return 0
        
        try:
            # Tentar extrair conteúdo completo usando extrator central
            from rb_ingestor.news_content_extractor import NewsContentExtractor
            extractor = NewsContentExtractor()
            url = news_article.get('link') or news_article.get('url', '')
            if url:
                self.stdout.write(f"🔍 Extraindo conteúdo completo via extrator: {url[:60]}...")
                extracted = extractor.extract_content_from_url(url)
                if extracted and extracted.get('content'):
                    self._base_news_text = extracted.get('content', '').strip()
                    word_count = len(self._base_news_text.split())
                    self.stdout.write(f"🔍 Conteúdo completo extraído: {word_count} palavras")
                    return word_count

            # Tentativa adicional: localizar URL original por título e fonte
            try:
                source_name = ''
                if news_article.get('source') and isinstance(news_article.get('source'), dict):
                    source_name = news_article.get('source', {}).get('title', '')
                title = news_article.get('title', '')
                original_url = extractor.find_original_url_by_title_and_source(title, source_name)
                if original_url:
                    self.stdout.write(f"🔗 URL original localizada por busca: {original_url}")
                    extracted = extractor.extract_content_from_url(original_url)
                    if extracted and extracted.get('content'):
                        self._base_news_text = extracted.get('content', '').strip()
                        word_count = len(self._base_news_text.split())
                        self.stdout.write(f"🔍 Conteúdo completo extraído: {word_count} palavras")
                        return word_count
            except Exception as e:
                self.stdout.write(f"⚠️ Falha na busca por título/fonte: {e}")

            # Fallback: usar título + descrição
            title = news_article.get('title', '')
            description = news_article.get('description', '')
            expanded_content = f"{title}\n{description}".strip()
            self._base_news_text = expanded_content
            word_count = len(expanded_content.split())
            self.stdout.write(f"📝 Conteúdo expandido (fallback): {word_count} palavras")
            return word_count
            
        except Exception as e:
            self.stdout.write(f"⚠️ Erro ao extrair conteúdo: {e}")
            return 0

    def _resolve_google_news_url(self, google_url):
        """Resolve URL do Google News para URL original"""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            response = requests.get(google_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Procurar por links que levam ao site original
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link.get('href')
                    if href and not 'news.google.com' in href and not 'google.com' in href:
                        if len(href) > 20:  # URLs muito curtos provavelmente não são notícias
                            return href
            
        except Exception as e:
            self.stdout.write(f"⚠️ Erro ao resolver URL: {e}")
        
        return None

    def _extract_content_from_url(self, url):
        """Extrai conteúdo de uma URL"""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remover scripts e estilos
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Extrair texto principal
                text = soup.get_text()
                return {'content': text}
                
        except Exception as e:
            self.stdout.write(f"⚠️ Erro ao extrair conteúdo da URL: {e}")
        
        return None

    def _has_openai_key(self):
        """Verifica se tem API key válida"""
        api_key = os.getenv('OPENAI_API_KEY')
        return api_key and len(api_key) > 20

    def _generate_with_ai_from_news(self, topic, news_article, min_words):
        """Gera conteúdo usando IA baseado na notícia encontrada"""
        self.stdout.write(f"🤖 Tentando gerar conteúdo com IA para '{topic}' (min: {min_words} palavras)")
        try:
            # Usar dados específicos da notícia
            title = news_article.get('title', '')
            description = news_article.get('description', '')
            published_date = news_article.get('published date', '')
            source = news_article.get('source', {}).get('title', '') if news_article.get('source') else ''
            base_text = getattr(self, '_base_news_text', '') or f"{title} {description}"
            
            prompt = f"""
            Papel: jornalista brasileiro sênior. Reescreva a notícia com naturalidade, precisão e SEO.

            Base (resumo factual – não copie literalmente):
            Título: {title}
            Descrição: {description}
            Data: {published_date}
            Fonte/portal: {source}
            Texto-base (trechos): \n{base_text[:5000]}

            Regras essenciais (responda exclusivamente em português do Brasil - pt-BR):
            - Reescreva completamente, sem copiar frases do original.
            - Linguagem clara e natural; evite jargões e clichês.
            - Traga contexto brasileiro quando fizer sentido.
            - Seja informativo: quem, o que, quando, onde, por quê, e o que muda.
            - Use subtítulos H2/H3 descritivos.
            - Inclua um bloco inicial de highlights (3–5 bullets) com fatos-chave.
            - Não mencione o nome do site fonte no título.
            - Mantenha o tamanho final EXATAMENTE entre {min_words} e {int(min_words*1.15)} palavras.
            - Evite repetição; não invente dados.
            - Não use palavras/frases em inglês (exceto termos técnicos já consagrados), mantenha todo o texto em pt-BR.

            Estrutura (EXATAMENTE 2 seções, DESENVOLVIDO):
            <h2>[Primeira Seção - Contexto e Desenvolvimentos]</h2>
            <p>[4-5 parágrafos informativos, cada um com 3-4 frases desenvolvidas]</p>
            
            <h2>[Segunda Seção - Análise e Perspectivas]</h2>
            <p>[4-5 parágrafos analíticos, cada um com 3-4 frases desenvolvidas]</p>

            REGRAS IMPORTANTES:
            - Desenvolva cada parágrafo com 3-4 frases completas
            - Cada seção deve ter pelo menos 4 parágrafos
            - Foque nas informações mais relevantes da notícia base
            - Expanda cada ponto com detalhes e contexto
            - Mantenha o número de palavras solicitado ({min_words} palavras)
            - Seja informativo e detalhado, mas direto ao ponto
            IMPORTANTE: 
            - NÃO use ```html ou ``` no início
            - NÃO use ... no final
            - Saída APENAS HTML puro, sem formatação markdown
            - Comece diretamente com <h2> e termine com </p>
            
            Saída: HTML enxuto (sem CSS, sem scripts), com parágrafos bem desenvolvidos e informativos.
            """
            
            # Usar prompt direto em vez da função generate_enhanced_article
            self.stdout.write("🔑 Verificando API key...")
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            self.stdout.write("📡 Enviando requisição para OpenAI...")
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um jornalista brasileiro especializado em criar artigos únicos e informativos."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            self.stdout.write("✅ Resposta recebida da OpenAI")
            content = response.choices[0].message.content
            self.stdout.write(f"📝 Conteúdo recebido: {len(content)} caracteres")
            
            # Processar resposta diretamente
            if content:
                # Limpar formatação markdown que possa ter escapado
                import re
                content = re.sub(r'^```html\s*', '', content)  # Remove ```html do início
                content = re.sub(r'```\s*$', '', content)      # Remove ``` do final
                content = re.sub(r'^\.\.\.\s*', '', content)   # Remove ... do início
                content = re.sub(r'\.\.\.\s*$', '', content)   # Remove ... do final
                content = content.strip()
                
                # Limpar HTML e extrair conteúdo para contagem
                clean_content = re.sub(r'<[^>]+>', ' ', content)
                word_count = len(clean_content.split())
                self.stdout.write(f"📊 Palavras contadas: {word_count} (mínimo necessário: {min_words * 0.9})")
                
                if word_count >= min_words * 0.8:  # Mais flexível: 80% do mínimo
                    self.stdout.write("✅ Conteúdo aprovado pela IA")
                    result = {'html': content}
                else:
                    self.stdout.write("❌ Conteúdo rejeitado por ter poucas palavras")
                    result = None
            else:
                result = None
            if result and isinstance(result, dict) and result.get('html'):
                html = result['html']
                # Pós-processamento: garantir teto de palavras
                import re
                text = strip_tags(html)
                target_max = int(min_words * 1.1)
                if len(text.split()) > target_max:
                    # cortar em limite de sentença
                    sentences = re.split(r'(?<=[\.!?])\s+', text)
                    acc = []
                    count = 0
                    for s in sentences:
                        w = len(s.split())
                        if count + w > target_max:
                            break
                        acc.append(s)
                        count += w
                    text = " ".join(acc).strip()
                    if not re.search(r'[\.!?]$', text):
                        text += '.'
                    html = f"<p>{text}</p>"
                return html
                
        except Exception as e:
            self.stdout.write(f"⚠️ Erro na IA: {e}")
            import traceback
            self.stdout.write(f"🔍 Traceback: {traceback.format_exc()}")
        
        return None

    def _determine_category(self, topic, content):
        """Determina categoria de forma simples"""
        try:
            from rb_noticias.models import Categoria
            
            # Tentar categorização inteligente
            from rb_ingestor.smart_categorizer import SmartCategorizer
            categorizer = SmartCategorizer()
            category_name = categorizer.categorize_content("", content, topic)
            
            # Buscar categoria existente (não criar novas)
            try:
                category = Categoria.objects.get(nome__iexact=category_name)
                self.stdout.write(f"📂 Categoria: {category.nome}")
                return category
            except Categoria.DoesNotExist:
                self.stdout.write(f"⚠️ Categoria '{category_name}' não existe; usando fallback")
                # Fallback para Brasil se existir, senão a primeira disponível
                try:
                    return Categoria.objects.get(nome__iexact='brasil')
                except Categoria.DoesNotExist:
                    return Categoria.objects.first()
                
        except Exception as e:
            self.stdout.write(f"⚠️ Erro na categorização: {e}")
            # Fallback para Brasil
            try:
                return Categoria.objects.get(nome__iexact='brasil')
            except Exception:
                return Categoria.objects.first()

    def _determine_category_with_publisher(self, topic, content, news_article):
        """Tenta usar categoria do publisher via extrator; se não houver, usa categorizador inteligente."""
        try:
            from rb_noticias.models import Categoria
            from rb_ingestor.news_content_extractor import NewsContentExtractor
            from rb_ingestor.smart_categorizer import SmartCategorizer
            extractor = NewsContentExtractor()
            # Se já temos link, extrair categoria diretamente
            link = news_article.get('link') or news_article.get('url')
            publisher_category = ''
            if link:
                data = extractor.extract_content_from_url(link)
                if data and isinstance(data, dict):
                    publisher_category = (data.get('category') or data.get('inferred_category') or '').strip()
            if publisher_category:
                try:
                    category = Categoria.objects.get(nome__iexact=publisher_category)
                    self.stdout.write(f"📂 Categoria (publisher): {category.nome}")
                    return category
                except Categoria.DoesNotExist:
                    self.stdout.write(f"⚠️ Categoria do publisher '{publisher_category}' não existe; usando categorizador inteligente")
            # Fallback: categorizador inteligente (sem criar categorias novas)
            try:
                categorizer = SmartCategorizer()
                category_name = categorizer.categorize_content("", content, topic)
                category = Categoria.objects.get(nome__iexact=category_name)
                self.stdout.write(f"📂 Categoria (inteligente): {category.nome}")
                return category
            except Exception:
                pass
            # Fallback final: Brasil ou primeira existente
            try:
                return Categoria.objects.get(nome__iexact='brasil')
            except Categoria.DoesNotExist:
                return Categoria.objects.first()
        except Exception as e:
            self.stdout.write(f"⚠️ Erro ao obter categoria do publisher: {e}")
            return self._determine_category(topic, content)

    def _publish_article(self, title, content, category, topic):
        """Publica o artigo"""
        Noticia = apps.get_model("rb_noticias", "Noticia")
        
        # Criar notícia
        noticia = Noticia.objects.create(
            titulo=title,
            conteudo=content,
            categoria=category,
            slug=f"{slugify(title)[:120]}-{timezone.now().strftime('%Y%m%d%H%M%S')}",
            status=Noticia.Status.PUBLICADO,
            publicado_em=timezone.now(),
            fonte_url=f"simple-{topic.lower().replace(' ', '-')}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        )
        
        # Adicionar imagem simples
        self._add_simple_image(noticia, topic)
        
        # Mostrar resultado
        word_count = len(strip_tags(content).split())
        self.stdout.write(f"📄 Título: {title}")
        self.stdout.write(f"📂 Categoria: {category.nome}")
        self.stdout.write(f"🔗 URL: /noticia/{noticia.slug}/")
        self.stdout.write(f"📊 Palavras: {word_count}")

    def _add_simple_image(self, noticia, topic):
        """Adiciona imagem usando Unsplash e Pexels APIs"""
        try:
            # Tentar Unsplash primeiro
            import requests
            unsplash_key = os.getenv('UNSPLASH_API_KEY', '')
            if unsplash_key:
                unsplash_url = "https://api.unsplash.com/search/photos"
                params = {
                    'query': f"{topic} brasil",
                    'per_page': 1,
                    'client_id': unsplash_key
                }
                response = requests.get(unsplash_url, params=params, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('results'):
                        photo = data['results'][0]
                        noticia.imagem = photo['urls']['regular']
                        noticia.imagem_alt = f"Imagem sobre {topic}"
                        noticia.imagem_credito = f"Foto: {photo['user']['name']} (Unsplash)"
                        noticia.imagem_fonte_url = photo['links']['html']
                        noticia.imagem_licenca = 'gratuita'
                        noticia.save()
                        self.stdout.write(f"🖼️ Imagem Unsplash: {photo['urls']['regular'][:50]}...")
                        return
            
            # Tentar Pexels se Unsplash falhar
            pexels_key = os.getenv('PEXELS_API_KEY', '')
            if pexels_key:
                pexels_url = "https://api.pexels.com/v1/search"
                headers = {'Authorization': pexels_key}
                params = {
                    'query': f"{topic} brasil",
                    'per_page': 1
                }
                response = requests.get(pexels_url, headers=headers, params=params, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('photos'):
                        photo = data['photos'][0]
                        noticia.imagem = photo['src']['large']
                        noticia.imagem_alt = f"Imagem sobre {topic}"
                        noticia.imagem_credito = f"Foto: {photo['photographer']} (Pexels)"
                        noticia.imagem_fonte_url = photo['url']
                        noticia.imagem_licenca = 'gratuita'
                        noticia.save()
                        self.stdout.write(f"🖼️ Imagem Pexels: {photo['src']['large'][:50]}...")
                        return

            # Fallback por categoria: URLs estáticas confiáveis (sem API)
            category_name = (noticia.categoria.nome if getattr(noticia, 'categoria', None) else '').lower()
            fallback_map = {
                'esportes': 'https://images.unsplash.com/photo-1517649763962-0c623066013b',
                'economia': 'https://images.unsplash.com/photo-1556740772-1a741367b93e',
                'política': 'https://images.unsplash.com/photo-1529101091764-c3526daf38fe',
                'mundo': 'https://images.unsplash.com/photo-1460899960812-f6ee1ecaf117',
                'brasil': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d'
            }
            fallback_url = fallback_map.get(category_name) or 'https://images.unsplash.com/photo-1477959858617-67f85cf4f1df'
            noticia.imagem = f"{fallback_url}?auto=format&fit=crop&w=1200&q=80"
            noticia.imagem_alt = f"Imagem ilustrativa sobre {noticia.categoria.nome if getattr(noticia, 'categoria', None) else topic}"
            noticia.imagem_credito = 'Unsplash (ilustrativa)'
            noticia.imagem_licenca = 'gratuita'
            noticia.save()
            self.stdout.write("🖼️ Imagem ilustrativa aplicada (fallback)")
        except Exception as e:
            self.stdout.write(f"⚠️ Erro ao adicionar imagem: {e}")
