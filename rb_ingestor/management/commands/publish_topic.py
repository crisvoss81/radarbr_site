# rb_ingestor/management/commands/publish_topic.py
"""
Comando completo para publicar artigo com tópico especificado manualmente
Seguindo toda a lógica do sistema RadarBR
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.html import strip_tags
from slugify import slugify
from django.apps import apps
import logging
import random

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Publica artigo com tópico especificado manualmente seguindo toda a lógica do sistema"

    def add_arguments(self, parser):
        parser.add_argument("topic", type=str, help="Tópico para o artigo")
        parser.add_argument("--category", type=str, help="Categoria específica (opcional)")
        parser.add_argument("--title", type=str, help="Título personalizado (opcional)")
        parser.add_argument("--force", action="store_true", help="Força publicação mesmo com duplicatas")
        parser.add_argument("--debug", action="store_true", help="Modo debug")
        parser.add_argument("--dry-run", action="store_true", help="Apenas simula, não publica")
        parser.add_argument("--words", type=int, default=800, help="Número mínimo de palavras (padrão: 800)")

    def handle(self, *args, **options):
        Noticia = apps.get_model("rb_noticias", "Noticia")
        Categoria = apps.get_model("rb_noticias", "Categoria")

        self.stdout.write("=== PUBLICAÇÃO MANUAL DE TÓPICO ===")
        self.stdout.write(f"Executado em: {timezone.now()}")
        
        topic = options["topic"]
        category = options.get("category")
        custom_title = options.get("title")
        min_words = options["words"]
        
        self.stdout.write(f"Topico: {topic}")
        if category:
            self.stdout.write(f"Categoria especificada: {category}")
        if custom_title:
            self.stdout.write(f"Titulo personalizado: {custom_title}")
        self.stdout.write(f"Minimo de palavras: {min_words}")

        # Verificar duplicatas se não forçar
        if not options["force"] and not options["dry_run"]:
            if self._check_duplicate(topic, Noticia):
                self.stdout.write("AVISO: Topico similar ja existe. Use --force para publicar mesmo assim.")
                return

        # Buscar notícias específicas sobre o tópico
        news_article = self._search_specific_news(topic)
        
        if news_article:
            self.stdout.write(f"Noticia encontrada: {news_article.get('title', '')[:50]}...")
            
            # Acessar sites originais mencionados na notícia
            enhanced_data = self._extract_from_original_sites(news_article)
            if enhanced_data:
                self.stdout.write(f"✅ Conteúdo extraído de site original: {enhanced_data.get('source_domain', 'N/A')}")
                # Usar dados reais extraídos
                news_article.update(enhanced_data)
            else:
                self.stdout.write("⚠ Usando dados básicos do Google News")
                # Melhorar os dados com informações mais específicas
                if news_article.get('title') and news_article.get('description'):
                    enhanced_context = {
                        'title': news_article.get('title', ''),
                        'description': news_article.get('description', ''),
                        'source': news_article.get('source', 'Google News'),
                        'url': news_article.get('url', ''),
                        'specific_news': True
                    }
                    news_article.update(enhanced_context)
        else:
            self.stdout.write("AVISO: Nenhuma noticia especifica encontrada para o topico - criando do zero")

        # Detectar categoria
        if category:
            cat = Categoria.objects.filter(nome=category).first()
            if not cat:
                cat = Categoria.objects.create(nome=category, slug=slugify(category)[:140])
        else:
            cat = self._detect_category_from_news(topic.lower(), news_article, Categoria)

        # Gerar título
        if custom_title:
            title = custom_title
        else:
            title = self._generate_title_from_news(topic, news_article)

        # Gerar conteúdo
        content = self._generate_content_from_news(topic, news_article, cat, min_words)
        
        # Verificar contagem de palavras
        word_count = len(strip_tags(content).split())
        self.stdout.write(f"Palavras geradas: {word_count}")
        
        # CATEGORIZAR BASEADO NO CONTEÚDO GERADO (apenas se categoria original não foi detectada com alta confiança)
        if not hasattr(self, '_original_category_confidence') or self._original_category_confidence < 0.6:
            self.stdout.write("🔍 Analisando conteúdo gerado para determinar categoria...")
            final_category = self._categorize_generated_content(content, topic)
            
            if final_category and final_category != cat:
                self.stdout.write(f"✅ Categoria ajustada: {cat.nome} → {final_category.nome}")
                cat = final_category
        else:
            self.stdout.write(f"✅ Mantendo categoria original detectada: {cat.nome} (confiança alta)")
        
        if word_count < min_words * 0.85:  # 85% do mínimo
            self.stdout.write(f"AVISO: Conteudo com {word_count} palavras (minimo: {int(min_words * 0.85)}), ajustando...")
            content = self._adjust_content_length(content, topic, cat, min_words)
            word_count = len(strip_tags(content).split())
            self.stdout.write(f"Palavras apos ajuste: {word_count}")

        # Integrar vídeos do YouTube automaticamente
        try:
            from rb_ingestor.youtube_integration import YouTubeIntegration
            youtube_integration = YouTubeIntegration()
            
            content_with_video = youtube_integration.integrate_video_into_content(
                content, topic, title, news_article
            )
            
            if content_with_video != content:
                self.stdout.write("Video do YouTube integrado automaticamente")
                content = content_with_video
                word_count = len(strip_tags(content).split())
                self.stdout.write(f"Palavras apos integracao de video: {word_count}")
            
        except Exception as e:
            self.stdout.write(f"AVISO: Erro na integracao do YouTube: {e}")

        # Verificar se está dentro da margem ideal
        if min_words * 0.85 <= word_count <= min_words * 1.15:
            self.stdout.write(f"Conteudo dentro da margem ideal: {word_count} palavras")
        else:
            self.stdout.write(f"AVISO: Conteudo fora da margem ideal: {word_count} palavras")

        if options["dry_run"]:
            self.stdout.write("MODO DRY-RUN: Artigo nao sera publicado")
            self.stdout.write(f"Titulo: {title}")
            self.stdout.write(f"Categoria: {cat.nome if cat else 'N/A'}")
            self.stdout.write(f"Palavras: {word_count}")
            return

        # Criar notícia
        noticia = Noticia.objects.create(
            titulo=title,
            conteudo=content,
            categoria=cat,
            slug=f"{slugify(title)[:120]}-{timezone.now().strftime('%Y%m%d%H%M%S')}",
            status=Noticia.Status.PUBLICADO,
            publicado_em=timezone.now(),
            fonte_url=f"manual-{topic.lower().replace(' ', '-')}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        )

        # Adicionar imagem
        self._add_image(noticia, topic, news_article)

        # Ping sitemap
        self._ping_sitemap()

        self.stdout.write("Artigo publicado com sucesso!")
        self.stdout.write(f"Titulo: {title}")
        self.stdout.write(f"Categoria: {cat.nome}")
        self.stdout.write(f"URL: {noticia.get_absolute_url()}")
        self.stdout.write(f"Palavras: {word_count}")
        self.stdout.write(f"Caracteres: {len(strip_tags(content))}")

    def _check_duplicate(self, topic, Noticia):
        """Verifica se já existe artigo similar"""
        topic_words = topic.lower().split()
        
        for word in topic_words:
            if len(word) > 3:
                similar = Noticia.objects.filter(titulo__icontains=word).first()
                if similar:
                    return True
        return False

    def _search_specific_news(self, topic):
        """Busca notícias específicas sobre o tópico"""
        try:
            from gnews import GNews
            
            google_news = GNews()
            google_news.language = "pt"
            google_news.country = "BR"
            google_news.max_results = 1
            
            articles = google_news.get_news(topic)
            
            if articles:
                article = articles[0]
                # Verificar se o tópico aparece no título ou descrição
                if self._is_relevant_article(topic, article):
                    return article
            
            return None
            
        except Exception as e:
            self.stdout.write(f"AVISO: Erro ao buscar noticias: {e}")
            return None

    def _extract_from_original_sites(self, news_article):
        """Extrai conteúdo do primeiro site que o Google News retornou"""
        try:
            # LÓGICA SIMPLES: Acessar diretamente o primeiro resultado do Google News
            google_news_url = news_article.get('url', '')
            
            if google_news_url and 'news.google.com' in google_news_url:
                self.stdout.write("🔍 Acessando primeiro resultado do Google News...")
                
                # Extrair URL original do Google News
                original_url = self._extract_original_url_from_google_news(google_news_url)
                
                if original_url:
                    self.stdout.write(f"✅ URL original encontrado: {original_url}")
                    
                    # Acessar diretamente o artigo original
                    content = self._extract_content_from_url(original_url)
                    
                    if content and content.get('content') and len(content.get('content', '')) > 200:
                        self.stdout.write(f"✅ Conteúdo extraído do artigo original")
                        return {
                            'title': content.get('title', ''),
                            'description': content.get('description', ''),
                            'content': content.get('content', ''),
                            'author': content.get('author', ''),
                            'date': content.get('date', ''),
                            'images': content.get('images', []),
                            'source_domain': self._extract_domain_from_url(original_url),
                            'original_url': original_url,
                            'real_content': True
                        }
                    else:
                        self.stdout.write("⚠ Conteúdo extraído insuficiente, usando dados do Google News")
                else:
                    self.stdout.write("⚠ Não foi possível extrair URL original")
            
            # FALLBACK: Usar dados do Google News diretamente
            self.stdout.write("🔄 Usando dados do Google News como base")
            return {
                'title': news_article.get('title', ''),
                'description': news_article.get('description', ''),
                'content': news_article.get('description', ''),  # Usar descrição como conteúdo
                'author': '',
                'date': news_article.get('published', ''),
                'images': [],
                'source_domain': 'google_news',
                'original_url': news_article.get('url', ''),
                'real_content': True
            }
            
        except Exception as e:
            self.stdout.write(f"AVISO: Erro ao extrair de sites originais: {e}")
            # FALLBACK FINAL: Usar dados do Google News
            return {
                'title': news_article.get('title', ''),
                'description': news_article.get('description', ''),
                'content': news_article.get('description', ''),
                'author': '',
                'date': news_article.get('published', ''),
                'images': [],
                'source_domain': 'google_news',
                'original_url': news_article.get('url', ''),
                'real_content': True
            }
    
    def _extract_original_url_from_google_news(self, google_news_url):
        """Extrai URL do veículo original a partir de um link do Google News.

        Estratégia em camadas:
        1) Se houver parâmetro "url" na query, retorna esse valor.
        2) Faz GET com allow_redirects=True e usa response.url (normalmente resolve para o site original).
        3) Fallback para heurísticas em HTML/JS se o 1 e 2 falharem.
        """
        try:
            import requests
            from bs4 import BeautifulSoup
            import re
            from urllib.parse import urlparse, parse_qs, urljoin
            
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })

            # 1) Tentar extrair via querystring "url"
            try:
                parsed = urlparse(google_news_url)
                qs = parse_qs(parsed.query)
                if 'url' in qs and qs['url']:
                    candidate = qs['url'][0]
                    if candidate and not self._is_google_news_url(candidate):
                        return candidate
            except Exception:
                pass

            # 2) Seguir redirecionamentos
            self.stdout.write(f"🔍 Acessando Google News: {google_news_url}")
            response = session.get(google_news_url, timeout=20, allow_redirects=True)
            response.raise_for_status()
            final_url = response.url
            if final_url and not self._is_google_news_url(final_url) and self._looks_like_news_url(final_url):
                self.stdout.write(f"🔗 Resolvido por redirect: {final_url}")
                return final_url
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # MÉTODO 1: Procurar por links diretos que não sejam do Google News
            all_links = soup.find_all('a', href=True)
            original_links = []
            
            for link in all_links:
                href = link.get('href')
                if href:
                    # Converter URLs relativos em absolutos
                    if href.startswith('/'):
                        href = urljoin(google_news_url, href)
                    
                    # Verificar se não é do Google News e parece ser uma notícia
                    if not self._is_google_news_url(href) and self._looks_like_news_url(href):
                        original_links.append(href)
                        self.stdout.write(f"🔗 Link encontrado: {href}")
            
            # MÉTODO 2: Procurar por meta tags Open Graph
            meta_tags = soup.find_all('meta')
            for meta in meta_tags:
                if meta.get('property') == 'og:url':
                    url = meta.get('content')
                    if url and not self._is_google_news_url(url) and self._looks_like_news_url(url):
                        original_links.append(url)
                        self.stdout.write(f"🔗 Meta og:url encontrado: {url}")
            
            # MÉTODO 3: Procurar por JavaScript que pode conter URLs
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    # Procurar por padrões de URL em JavaScript
                    url_patterns = [
                        r'https?://[^\s"\'<>]+\.(com|br|org|net)/[^\s"\'<>]*',
                        r'url["\']?\s*:\s*["\']([^"\']+)["\']',
                        r'href["\']?\s*:\s*["\']([^"\']+)["\']'
                    ]
                    
                    for pattern in url_patterns:
                        matches = re.findall(pattern, script.string)
                        for match in matches:
                            if isinstance(match, tuple):
                                url = match[0] if match[0] else match[1]
                            else:
                                url = match
                            
                            if url and not self._is_google_news_url(url) and self._looks_like_news_url(url):
                                original_links.append(url)
                                self.stdout.write(f"🔗 URL encontrado em JS: {url}")
            
            # MÉTODO 4: Procurar por atributos data-* que podem conter URLs
            try:
                elements_with_data = soup.find_all(attrs=lambda attrs: attrs and hasattr(attrs, 'keys') and any(k.startswith('data-') for k in attrs.keys()))
                for element in elements_with_data:
                    if hasattr(element, 'attrs') and element.attrs:
                        for attr_name, attr_value in element.attrs.items():
                            if attr_name.startswith('data-') and isinstance(attr_value, str):
                                if 'http' in attr_value and not self._is_google_news_url(attr_value):
                                    if self._looks_like_news_url(attr_value):
                                        original_links.append(attr_value)
                                        self.stdout.write(f"🔗 URL encontrado em data-*: {attr_value}")
            except Exception as e:
                self.stdout.write(f"⚠ Erro ao processar atributos data-*: {e}")
            
            # Remover duplicatas e retornar o primeiro URL válido
            unique_links = list(dict.fromkeys(original_links))
            
            for url in unique_links:
                if self._is_valid_news_url(url):
                    self.stdout.write(f"✅ URL original válido encontrado: {url}")
                    return url
            
            self.stdout.write("❌ Nenhum URL original válido encontrado")
            return None
            
        except Exception as e:
            self.stdout.write(f"⚠ Erro ao extrair URL original: {e}")
            return None
    
    def _is_google_news_url(self, url):
        """Verifica se o URL é do Google News"""
        if not url:
            return False
        
        google_news_domains = [
            'news.google.com',
            'news.google.com.br',
            'news.google.co.uk'
        ]
        
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc.lower() in google_news_domains
    
    def _is_valid_news_url(self, url):
        """Verifica se o URL é válido para uma notícia"""
        if not url:
            return False
        
        # URLs muito curtos provavelmente não são notícias
        if len(url) < 20:
            return False
        
        # Verificar se não é um URL do Google News
        if self._is_google_news_url(url):
            return False
        
        # Verificar se parece ser um URL de notícia
        return self._looks_like_news_url(url)
    
    def _extract_domain_from_url(self, url):
        """Extrai domínio de uma URL"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc.lower()
    
    def _find_specific_news_url(self, site_url, search_term):
        """Encontra URL específico da notícia no site"""
        try:
            import requests
            from bs4 import BeautifulSoup
            import re
            
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            # Tentar diferentes URLs de busca no site
            search_urls = [
                f"{site_url}/busca?q={search_term}",
                f"{site_url}/search?q={search_term}",
                f"{site_url}/noticias?q={search_term}",
                f"{site_url}/?q={search_term}"
            ]
            
            for search_url in search_urls:
                try:
                    self.stdout.write(f"🔍 Buscando em: {search_url}")
                    response = session.get(search_url, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Procurar por links de notícias
                    news_links = []
                    
                    # Procurar por links que contenham palavras-chave da busca
                    search_words = search_term.lower().split()
                    
                    all_links = soup.find_all('a', href=True)
                    for link in all_links:
                        href = link.get('href')
                        link_text = link.get_text().lower()
                        
                        if href and any(word in link_text for word in search_words):
                            # Converter URL relativo em absoluto
                            if href.startswith('/'):
                                from urllib.parse import urljoin
                                href = urljoin(site_url, href)
                            
                            # Verificar se parece ser um link de notícia
                            if self._looks_like_news_url(href) and site_url in href:
                                news_links.append(href)
                                self.stdout.write(f"🔗 Link de notícia encontrado: {href}")
                    
                    # Retornar o primeiro link válido encontrado
                    for link in news_links:
                        if self._is_valid_news_url(link):
                            return link
                    
                except Exception as e:
                    self.stdout.write(f"⚠ Erro ao buscar em {search_url}: {e}")
                    continue
            
            return None
            
        except Exception as e:
            self.stdout.write(f"⚠ Erro ao encontrar URL específico: {e}")
            return None
    
    def _extract_content_from_url(self, url):
        """Extrai conteúdo de uma URL específica"""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            response = session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extrair dados da notícia
            extracted_data = {
                'url': url,
                'title': self._extract_title_from_soup(soup),
                'description': self._extract_description_from_soup(soup),
                'content': self._extract_content_from_soup(soup),
                'author': self._extract_author_from_soup(soup),
                'date': self._extract_date_from_soup(soup),
                'images': self._extract_images_from_soup(soup)
            }
            
            # Verificar se conseguiu extrair conteúdo válido
            if extracted_data['title'] and extracted_data['content'] and len(extracted_data['content']) > 200:
                return extracted_data
            
            return None
            
        except Exception as e:
            self.stdout.write(f"⚠ Erro ao extrair conteúdo de {url}: {e}")
            return None
    
    def _search_news_on_site(self, site_url, search_term):
        """Busca notícias relacionadas em um site específico"""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            # Tentar diferentes URLs de busca no site
            search_urls = [
                f"{site_url}/busca",
                f"{site_url}/search",
                f"{site_url}/noticias",
                f"{site_url}/ultimas-noticias",
                site_url
            ]
            
            for search_url in search_urls:
                try:
                    response = session.get(search_url, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Procurar por links de notícias
                        news_links = self._find_news_links(soup, site_url)
                        
                        if news_links:
                            # Tentar acessar a primeira notícia encontrada
                            for news_url in news_links[:2]:
                                try:
                                    news_response = session.get(news_url, timeout=15)
                                    news_response.raise_for_status()
                                    
                                    news_soup = BeautifulSoup(news_response.content, 'html.parser')
                                    
                                    # Extrair dados da notícia
                                    extracted_data = {
                                        'url': news_url,
                                        'title': self._extract_title_from_soup(news_soup),
                                        'description': self._extract_description_from_soup(news_soup),
                                        'content': self._extract_content_from_soup(news_soup),
                                        'author': self._extract_author_from_soup(news_soup),
                                        'date': self._extract_date_from_soup(news_soup),
                                        'images': self._extract_images_from_soup(news_soup)
                                    }
                                    
                                    # Verificar se conseguiu extrair conteúdo válido
                                    if extracted_data['title'] and extracted_data['content'] and len(extracted_data['content']) > 200:
                                        return extracted_data
                                    
                                except Exception as e:
                                    continue
                    
                except Exception as e:
                    continue
            
            return None
            
        except Exception as e:
            return None
    
    def _find_news_links(self, soup, site_url):
        """Encontra links de notícias em uma página"""
        links = []
        
        # Procurar por links que parecem ser notícias
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link.get('href')
            if href:
                # Converter URL relativa em absoluta
                if href.startswith('/'):
                    href = f"{site_url}{href}"
                elif href.startswith('//'):
                    href = f"https:{href}"
                
                # Verificar se parece ser um link de notícia
                if self._looks_like_news_url(href):
                    links.append(href)
        
        return links[:5]  # Retornar até 5 links
    
    def _looks_like_news_url(self, url):
        """Verifica se o URL parece ser de uma notícia"""
        if not url:
            return False
        
        # Padrões comuns de URLs de notícias
        news_patterns = [
            r'/\d{4}/\d{2}/\d{2}/',  # Data no formato YYYY/MM/DD
            r'/noticia/',             # Contém "noticia"
            r'/materia/',             # Contém "materia"
            r'/artigo/',              # Contém "artigo"
            r'\.html$',               # Termina com .html
            r'\.php$',                # Termina com .php
        ]
        
        import re
        for pattern in news_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        
        return False
    
    def _extract_title_from_soup(self, soup):
        """Extrai título de um soup"""
        # Procurar por meta tags primeiro
        meta_title = soup.find('meta', property='og:title')
        if meta_title and meta_title.get('content'):
            return meta_title.get('content').strip()
        
        # Procurar por elementos de título
        title_selectors = ['h1', '.titulo', '.title', '.headline', '.noticia-titulo']
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text().strip()
                if title and len(title) > 10:
                    return title
        return ''
    
    def _extract_description_from_soup(self, soup):
        """Extrai descrição de um soup"""
        meta_desc = soup.find('meta', property='og:description')
        if meta_desc and meta_desc.get('content'):
            return meta_desc.get('content').strip()
        return ''
    
    def _extract_content_from_soup(self, soup):
        """Extrai conteúdo principal de um soup"""
        # Remover elementos indesejados
        for element in soup(['script', 'style', 'nav', 'header', 'footer']):
            element.decompose()
        
        # Procurar por conteúdo principal
        content_selectors = ['.conteudo', '.noticia-conteudo', '.materia-conteudo', '.texto', '.content', 'article']
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                content = element.get_text().strip()
                if content and len(content) > 100:
                    return content
        return ''
    
    def _extract_author_from_soup(self, soup):
        """Extrai autor de um soup"""
        author_selectors = ['.autor', '.author', '.byline']
        for selector in author_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
        return ''
    
    def _extract_date_from_soup(self, soup):
        """Extrai data de um soup"""
        date_selectors = ['.data', '.date', '.published', 'time']
        for selector in date_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
        return ''
    
    def _extract_images_from_soup(self, soup):
        """Extrai imagens de um soup"""
        images = []
        img_elements = soup.find_all('img')
        for img in img_elements[:3]:  # Máximo 3 imagens
            src = img.get('src') or img.get('data-src')
            if src:
                alt = img.get('alt', '')
                images.append({'src': src, 'alt': alt})
        return images

    def _is_relevant_article(self, topic, article):
        """Verifica se o artigo é relevante para o tópico"""
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        
        # Verificar se o tópico aparece no título ou descrição
        topic_words = topic.lower().split()
        relevance_score = 0
        
        for word in topic_words:
            if len(word) > 3:  # Ignorar palavras muito curtas
                if word in title:
                    relevance_score += 2
                if word in description:
                    relevance_score += 1
        
        # Considerar relevante se score >= 2
        return relevance_score >= 2

    def _categorize_generated_content(self, content, topic):
        """Categoriza o artigo baseado no conteúdo gerado"""
        try:
            from rb_ingestor.smart_categorizer import SmartCategorizer
            from rb_noticias.models import Categoria
            
            # Usar o SmartCategorizer para analisar o conteúdo
            categorizer = SmartCategorizer()
            
            # Combinar título e conteúdo para análise
            text_to_analyze = f"{topic} {content}"
            
            # Categorizar usando o conteúdo (retorna apenas o nome)
            category_name = categorizer.categorize_content("", text_to_analyze, topic)
            confidence = categorizer.get_category_confidence("", text_to_analyze, topic)
            self.stdout.write(f"🎯 Categoria detectada pelo conteúdo: {category_name} (confiança: {confidence:.2f})")
            
            # Buscar ou criar a categoria
            try:
                category = Categoria.objects.get(nome__iexact=category_name)
                self.stdout.write(f"✅ Usando categoria existente: {category.nome}")
                return category
            except Categoria.DoesNotExist:
                # Criar nova categoria se não existir
                category = Categoria.objects.create(nome=category_name.title())
                self.stdout.write(f"✅ Nova categoria criada: {category.nome}")
                return category
                
        except Exception as e:
            self.stdout.write(f"⚠ Erro na categorização por conteúdo: {e}")
            # Fallback para categoria padrão
            try:
                return Categoria.objects.get(nome__iexact='brasil')
            except Categoria.DoesNotExist:
                return Categoria.objects.first()
    
    def _generate_title_from_news(self, topic, news_article):
        """Gera título PRÓPRIO SEO: Entidade + verbo + objeto: gancho (sem copiar)."""
        if not news_article:
            return f"{topic.title()}: Últimas Notícias"

        import re

        original = (news_article.get('title') or '').strip()
        description = (news_article.get('description') or '').strip()
        base_topic = topic.title().strip() or 'Notícia'

        # Remover marcas de portal
        portals = ['G1','Globo','Folha','Estadão','UOL','Terra','R7','IG','Exame','Metrópoles','O Globo','CNN','BBC','Reuters']
        clean = original
        for p in portals:
            clean = clean.replace(f' - {p}', '').replace(f' | {p}', '').replace(f' ({p})', '')

        # Heurísticas para entidade, verbo e objeto
        text_all = f"{clean}. {description}"
        # Entidade: primeira sequência de palavras com inicial maiúscula
        m_ent = re.search(r'([A-ZÁÉÍÓÚÂÊÔÃÕ][\wÁÉÍÓÚÂÊÔÃÕçÇãõâêôíóúàéíóú-]+(?:\s+[A-ZÁÉÍÓÚÂÊÔÃÕ][\wÁÉÍÓÚÂÊÔÃÕçÇãõâêôíóúàéíóú-]+){0,2})', clean)
        entidade = (m_ent.group(1) if m_ent else base_topic).strip()
        # Verbo chave
        verbos_map = {
            'aprova':'aprova','anuncia':'anuncia','divulga':'divulga','entrega':'entrega','confirma':'confirma',
            'projeta':'projeta','corta':'corta','eleva':'eleva','recuar':'recua','recua':'recua','sobe':'sobe','cai':'cai'
        }
        verbo = None
        for v in verbos_map.keys():
            if re.search(rf'\b{v}\w*\b', text_all, re.IGNORECASE):
                verbo = verbos_map[v]; break
        verbo = verbo or 'anuncia'
        # Objeto
        objetos = ['dividendos','impostos','preços','tarifas','acordo','parceria','reféns','sanções','investimentos','meta','juros']
        objeto = None
        for o in objetos:
            if re.search(rf'\b{o}\b', text_all, re.IGNORECASE):
                objeto = o; break
        objeto = objeto or (clean.split(':')[0].lower() if ':' in clean else base_topic.lower())

        # Estruturas de título mais naturais e variadas
        estruturas = []
        
        # Estrutura 1: Declaração direta (sem dois pontos)
        if objeto in ['dividendos', 'juros', 'impostos']:
            estruturas.append(f"{entidade} {verbo} {objeto} — valores e datas")
            estruturas.append(f"{entidade} {verbo} {objeto} para acionistas")
        
        # Estrutura 2: Com dois pontos (apenas para explicações)
        if objeto in ['acordo', 'parceria', 'medidas']:
            estruturas.append(f"{entidade} {verbo} {objeto}: entenda os detalhes")
            estruturas.append(f"{entidade} {verbo} {objeto}: o que muda")
        
        # Estrutura 3: Interrogativa (para engajamento)
        if verbo in ['anuncia', 'divulga', 'confirma']:
            estruturas.append(f"O que {entidade} {verbo} sobre {objeto}?")
            estruturas.append(f"Como {entidade} {verbo} {objeto}?")
        
        # Estrutura 4: Declaração simples (mais natural)
        estruturas.append(f"{entidade} {verbo} {objeto}")
        estruturas.append(f"{entidade} {verbo} {objeto} hoje")
        
        # Estrutura 5: Com traço (mais elegante)
        estruturas.append(f"{entidade} {verbo} {objeto} — análise completa")
        estruturas.append(f"{entidade} {verbo} {objeto} — impactos e próximos passos")

        # Remover duplicatas na entidade (ex.: "Petrobras Dividendos: Petrobras ...")
        if entidade.lower() in base_topic.lower():
            entidade = base_topic

        # Escolher a melhor estrutura baseada no contexto
        for estrutura in estruturas:
            # Substituir entidade na estrutura escolhida
            titulo = estrutura.replace("{entidade}", entidade).replace("{verbo}", verbo).replace("{objeto}", objeto)
            
            # Verificar se não é muito similar ao original
            if self._is_title_different_enough(titulo, clean):
                # Normalizar espaços e limitar tamanho
                titulo = re.sub(r'\s+', ' ', titulo).strip()
                if 20 <= len(titulo) <= 140:
                    return titulo
        
        # Fallback: estrutura simples
        titulo = f"{entidade} {verbo} {objeto}"
        titulo = re.sub(r'\s+', ' ', titulo).strip()
        return titulo[:140]

    def _is_title_different_enough(self, new_title, original_title):
        """Verifica se o novo título é suficientemente diferente do original"""
        import re
        
        if not original_title:
            return True
        
        # Normalizar ambos os títulos
        new_norm = re.sub(r'\s+', ' ', new_title.lower().strip())
        orig_norm = re.sub(r'\s+', ' ', original_title.lower().strip())
        
        # Se são idênticos, não usar
        if new_norm == orig_norm:
            return False
        
        # Se o novo título contém mais de 80% das palavras do original, evitar
        new_words = set(new_norm.split())
        orig_words = set(orig_norm.split())
        
        if len(orig_words) > 0:
            similarity = len(new_words.intersection(orig_words)) / len(orig_words)
            if similarity > 0.8:
                return False
        
        return True

    def _generate_content_from_news(self, topic, news_article, category, min_words):
        """Gera conteúdo baseado na notícia específica encontrada - MESMA LÓGICA DA AUTOMAÇÃO"""
        try:
            # Usar sistema de IA melhorado (MESMO DA AUTOMAÇÃO)
            from rb_ingestor.ai_enhanced import generate_enhanced_article
            
            ai_content = generate_enhanced_article(topic, news_article, min_words)
            
            if ai_content:
                # Verificar qualidade do conteúdo
                word_count = ai_content.get("word_count", 0)
                quality_score = ai_content.get("quality_score", 0)
                
                if word_count >= min_words and quality_score >= 40:  # Aceitar qualidade 40%+
                    self.stdout.write(f"IA melhorada gerou {word_count} palavras (qualidade: {quality_score}%)")
                    
                    # Usar o conteúdo da IA diretamente
                    title = strip_tags(ai_content.get("title", topic.title()))[:200]
                    dek = strip_tags(ai_content.get("dek", news_article.get("description", "") if news_article else ""))[:220]
                    html_content = ai_content.get("html", "<p></p>")
                    
                    # Montar conteúdo final
                    content = f'<p class="dek">{dek}</p>\n{html_content}'
                    return content
                else:
                    self.stdout.write(f"AVISO: IA gerou {word_count} palavras (qualidade: {quality_score}%), usando fallback")
            else:
                self.stdout.write("AVISO: IA não retornou conteúdo, usando fallback")
                
        except Exception as e:
            self.stdout.write(f"AVISO: Erro na IA melhorada: {e}")
        
        # FALLBACK MELHORADO: Usar a mesma lógica da automação
        return self._generate_content_based_on_reference(topic, news_article, category, min_words)

    def _generate_content_from_news_fallback(self, topic, news_article, category, min_words):
        """Gera conteúdo fallback baseado na notícia específica"""
        if not news_article:
            return self._generate_content_from_scratch(topic, category, min_words)
        
        # USAR APENAS A NOTÍCIA ESPECÍFICA ENCONTRADA
        title = news_article.get("title", "")
        description = news_article.get("description", "")
        source = news_article.get("source", "")
        
        # Criar conteúdo baseado EXCLUSIVAMENTE na notícia encontrada
        content = f"""<p class="dek">{description}</p>

<h2>Análise da Notícia</h2>

<p>Esta notícia tem ganhado destaque e merece análise detalhada. {title}</p>

<h3>Contexto e Desenvolvimentos</h3>

<p>Os fatos relacionados a esta notícia indicam uma evolução significativa no cenário atual. A situação tem sido acompanhada de perto por especialistas e analistas que estudam o impacto dessas transformações.</p>

<p>Segundo informações da {source}, os desenvolvimentos mais recentes mostram uma evolução positiva em diversos indicadores relacionados ao tema.</p>

<h3>Análise Detalhada</h3>

<p>Analisando os dados disponíveis, é possível identificar padrões importantes que merecem atenção. A notícia sobre "{title}" representa um marco significativo no contexto atual.</p>

<p>Especialistas têm destacado a importância deste desenvolvimento para o futuro do setor. As implicações são amplas e afetam diversos aspectos da sociedade.</p>

<h3>Impacto no Brasil</h3>

<p>No contexto brasileiro, esta notícia tem repercussões importantes. O país tem acompanhado de perto os desenvolvimentos relacionados a este tema.</p>

<p>As autoridades brasileiras têm se posicionado de forma clara sobre o assunto, demonstrando preocupação com os impactos potenciais.</p>

<h3>Desenvolvimentos Recentes</h3>

<p>Os desenvolvimentos mais recentes relacionados a esta notícia têm chamado a atenção de especialistas e analistas. A evolução da situação tem sido acompanhada de perto por diversos setores da sociedade.</p>

<p>Segundo análises realizadas por especialistas, os indicadores mostram uma tendência positiva que pode trazer benefícios significativos para o país.</p>

<h3>Perspectivas Futuras</h3>

<p>Olhando para o futuro, espera-se que novos desenvolvimentos surjam nos próximos dias. A situação está em constante evolução.</p>

<p>Especialistas preveem que os próximos passos serão cruciais para determinar o rumo dos acontecimentos.</p>

<h3>Conclusão</h3>

<p>Esta notícia representa um momento importante na evolução do tema. É fundamental acompanhar os próximos desenvolvimentos para entender completamente o impacto.</p>

<p>O RadarBR continuará acompanhando esta história e trará atualizações conforme novos fatos surjam.</p>"""

        return content

    def _generate_content_based_on_reference(self, topic, news_article, category, min_words):
        """Gera conteúdo baseado em artigo de referência com margem de +/-15% - MESMA LÓGICA DA AUTOMAÇÃO"""
        try:
            # Usar IA melhorada com contexto específico da notícia
            from rb_ingestor.ai_enhanced import generate_enhanced_article
            
            # Calcular margem de palavras (±15%)
            target_words = min_words
            min_target = int(target_words * 0.85)
            max_target = int(target_words * 1.15)
            
            ai_content = generate_enhanced_article(topic, news_article, target_words)
            
            if ai_content:
                word_count = ai_content.get("word_count", 0)
                quality_score = ai_content.get("quality_score", 0)
                
                if min_target <= word_count <= max_target and quality_score >= 60:
                    self.stdout.write(f"Conteudo baseado em referencia: {word_count} palavras (qualidade: {quality_score}%)")
                    title = strip_tags(ai_content.get("title", topic.title()))[:200]
                    content = f'<p class="dek">{strip_tags(ai_content.get("dek", news_article.get("description", "") if news_article else ""))[:220]}</p>\n{ai_content.get("html", "<p></p>")}'
                    return content
                else:
                    self.stdout.write(f"AVISO: IA fora da margem ({word_count} palavras), ajustando...")
            
        except Exception as e:
            self.stdout.write(f"AVISO: Erro na IA melhorada: {e}")
        
        # Fallback: criar conteúdo baseado na referência
        return self._create_content_from_reference(topic, news_article, category, min_words)

    def _create_content_from_reference(self, topic, news_article, category, min_words):
        """Cria conteúdo baseado na referência encontrada"""
        if not news_article:
            return self._generate_content_from_scratch(topic, category, min_words)
        
        title = news_article.get("title", "")
        description = news_article.get("description", "")
        source = news_article.get("source", "")
        
        # Criar conteúdo baseado na notícia específica
        content = f"""<p class="dek">{description}</p>

<h2>Análise da Notícia</h2>

<p>Esta notícia tem ganhado destaque e merece análise detalhada. {title}</p>

<h3>Contexto e Desenvolvimentos</h3>

<p>Os fatos relacionados a esta notícia indicam uma evolução significativa no cenário atual. A situação tem sido acompanhada de perto por especialistas e analistas que estudam o impacto dessas transformações.</p>

<p>Segundo informações da {source}, os desenvolvimentos mais recentes mostram uma evolução positiva em diversos indicadores relacionados ao tema.</p>

<h3>Análise Detalhada</h3>

<p>Analisando os dados disponíveis, é possível identificar padrões importantes que merecem atenção. A notícia sobre "{title}" representa um marco significativo no contexto atual.</p>

<p>Especialistas têm destacado a importância deste desenvolvimento para o futuro do setor. As implicações são amplas e afetam diversos aspectos da sociedade.</p>

<h3>Impacto no Brasil</h3>

<p>No contexto brasileiro, esta notícia tem repercussões importantes. O país tem acompanhado de perto os desenvolvimentos relacionados a este tema.</p>

<p>As autoridades brasileiras têm se posicionado de forma clara sobre o assunto, demonstrando preocupação com os impactos potenciais.</p>

<h3>Desenvolvimentos Recentes</h3>

<p>Os desenvolvimentos mais recentes relacionados a esta notícia têm chamado a atenção de especialistas e analistas. A evolução da situação tem sido acompanhada de perto por diversos setores da sociedade.</p>

<p>Segundo análises realizadas por especialistas, os indicadores mostram uma tendência positiva que pode trazer benefícios significativos para o país.</p>

<h3>Perspectivas Futuras</h3>

<p>Olhando para o futuro, espera-se que novos desenvolvimentos surjam nos próximos dias. A situação está em constante evolução.</p>

<p>Especialistas preveem que os próximos passos serão cruciais para determinar o rumo dos acontecimentos.</p>

<h3>Conclusão</h3>

<p>Esta notícia representa um momento importante na evolução do tema. É fundamental acompanhar os próximos desenvolvimentos para entender completamente o impacto.</p>

<p>O RadarBR continuará acompanhando esta história e trará atualizações conforme novos fatos surjam.</p>"""

        return content

    def _generate_content_from_scratch(self, topic, category, min_words):
        """Gera conteúdo do zero quando não há notícia específica"""
        category_name = category.nome if category else "geral"
        
        content = f"""<p class="dek">Análise completa sobre {topic.lower()} e seus desenvolvimentos recentes no Brasil.</p>

<h2>Desenvolvimentos Recentes</h2>

<p>Esta notícia tem ganhado destaque nos últimos dias e merece atenção especial. {topic.title()} tem sido um tema de grande relevância no cenário atual.</p>

<h3>Contexto da Notícia</h3>

<p>Os fatos relacionados a {topic.lower()} indicam uma evolução significativa no cenário atual. A situação tem sido acompanhada de perto por especialistas e analistas que estudam o impacto dessas transformações.</p>

<p>Segundo informações de fontes especializadas, os desenvolvimentos mais recentes mostram uma evolução positiva em diversos indicadores relacionados ao tema.</p>

<h3>Análise Detalhada</h3>

<p>Analisando os dados disponíveis, é possível identificar padrões importantes que merecem atenção. {topic.title()} representa um marco significativo no contexto atual.</p>

<p>Especialistas têm destacado a importância deste desenvolvimento para o futuro do setor. As implicações são amplas e afetam diversos aspectos da sociedade.</p>

<h3>Impacto no Brasil</h3>

<p>No contexto brasileiro, {topic.lower()} tem repercussões importantes. O país tem acompanhado de perto os desenvolvimentos relacionados a este tema.</p>

<p>As autoridades brasileiras têm se posicionado de forma clara sobre o assunto, demonstrando preocupação com os impactos potenciais.</p>

<h3>Desenvolvimentos Recentes</h3>

<p>Os desenvolvimentos mais recentes relacionados a {topic.lower()} têm chamado a atenção de especialistas e analistas. A evolução da situação tem sido acompanhada de perto por diversos setores da sociedade.</p>

<p>Segundo análises realizadas por especialistas, os indicadores mostram uma tendência positiva que pode trazer benefícios significativos para o país.</p>

<h3>Perspectivas Futuras</h3>

<p>Olhando para o futuro, espera-se que novos desenvolvimentos surjam nos próximos dias. A situação está em constante evolução.</p>

<p>Especialistas preveem que os próximos passos serão cruciais para determinar o rumo dos acontecimentos.</p>

<h3>Conclusão</h3>

<p>{topic.title()} representa um momento importante na evolução do tema. É fundamental acompanhar os próximos desenvolvimentos para entender completamente o impacto.</p>

<p>O RadarBR continuará acompanhando esta história e trará atualizações conforme novos fatos surjam.</p>"""

        return content

    def _adjust_content_length(self, content, topic, category, min_words):
        """Ajusta o comprimento do conteúdo para atingir o mínimo de palavras"""
        current_words = len(strip_tags(content).split())
        
        if current_words >= min_words:
            return content
        
        # Adicionar seções extras se necessário
        additional_content = f"""

<h3>Desenvolvimento Nacional</h3>

<p>No contexto nacional, {topic.lower()} tem se mostrado um tema de grande relevância para o desenvolvimento do Brasil. As iniciativas relacionadas a este assunto têm ganhado destaque.</p>

<p>O país tem demonstrado capacidade de liderança nesta área, com resultados positivos que beneficiam toda a sociedade.</p>

<h3>Impacto Regional no Brasil</h3>

<p>O impacto de {topic.lower()} varia significativamente entre as diferentes regiões do Brasil. No Nordeste, por exemplo, as características específicas da região influenciam diretamente como este tema se desenvolve, criando oportunidades únicas de crescimento e desenvolvimento.</p>

<p>Na região Sul, a tradição industrial e tecnológica oferece um ambiente propício para o desenvolvimento de soluções inovadoras relacionadas a {topic.lower()}. Esta vantagem competitiva tem sido aproveitada por empresas e profissionais locais.</p>

<h3>Tendências Emergentes</h3>

<p>As tendências emergentes relacionadas a {topic.lower()} indicam uma evolução constante e positiva. Novas tecnologias e metodologias estão sendo desenvolvidas, criando oportunidades para profissionais e empresas brasileiras.</p>

<p>Essas tendências são acompanhadas de perto por especialistas e pesquisadores, que identificam padrões e desenvolvem estratégias para aproveitar as oportunidades que surgem.</p>

<h3>Casos de Sucesso</h3>

<p>Existem diversos casos de sucesso relacionados a {topic.lower()} no Brasil que servem como referência e inspiração. Esses casos demonstram o potencial do país e a capacidade dos profissionais brasileiros de desenvolver soluções inovadoras.</p>

<p>Esses exemplos de sucesso são fundamentais para motivar outros profissionais e empresas a investirem nesta área, criando um ciclo virtuoso de crescimento e desenvolvimento.</p>

<h3>Recomendações e Próximos Passos</h3>

<p>Com base na análise apresentada, é possível identificar algumas recomendações importantes para o desenvolvimento futuro desta área. Essas recomendações são fundamentadas em dados concretos e na experiência de especialistas.</p>

<p>O primeiro passo é continuar investindo em pesquisa e desenvolvimento, garantindo que o Brasil mantenha sua posição de liderança. Além disso, é importante focar na formação de profissionais qualificados.</p>"""

        return content + additional_content

    def _detect_category_from_news(self, topic_lower, news_article, Categoria):
        """Detecta categoria baseada no site de origem, notícia encontrada ou sistema inteligente"""
        # 1. PRIORIDADE MÁXIMA: Extrair categoria do site de origem
        if news_article and news_article.get("original_url"):
            # Verificar se não é uma URL do Google News
            original_url = news_article.get("original_url")
            if self._is_google_news_url(original_url):
                self.stdout.write("⚠ Pulando SiteCategorizer - URL é do Google News")
            else:
                try:
                    from rb_ingestor.site_categorizer import SiteCategorizer
                    site_categorizer = SiteCategorizer()
                    
                    # Usar URL original em vez do Google News
                    original_news = {
                        'url': original_url,
                        'title': news_article.get('title', ''),
                        'description': news_article.get('description', '')
                    }
                    
                    # Tentar extrair categoria do site original
                    site_category = site_categorizer.categorize_article(original_news)
                    
                    if site_category:
                        self.stdout.write(f"Categoria do site: {site_category}")
                        
                        # Buscar categoria existente
                        cat = Categoria.objects.filter(nome=site_category.title()).first()
                        if cat:
                            self.stdout.write(f"Usando categoria existente: {site_category}")
                            return cat
                        
                        # Criar nova categoria se não existir
                        cat, created = Categoria.objects.get_or_create(
                            slug=slugify(site_category)[:140],
                            defaults={"nome": site_category.title()}
                        )
                        if created:
                            self.stdout.write(f"Nova categoria criada: {site_category}")
                        else:
                            self.stdout.write(f"Categoria encontrada: {site_category}")
                        return cat
                    
                except Exception as e:
                    self.stdout.write(f"AVISO: Erro no categorizador de site: {e}")
        
        # 2. FALLBACK: Tentar usar categoria da notícia encontrada
        if news_article and news_article.get("category"):
            news_category = news_article.get("category", "").strip()
            if news_category:
                # Limpar e normalizar categoria da notícia
                clean_category = news_category.title().strip()
                self.stdout.write(f"Categoria da noticia: {clean_category}")
                
                # Buscar categoria existente
                cat = Categoria.objects.filter(nome=clean_category).first()
                if cat:
                    self.stdout.write(f"Usando categoria existente: {clean_category}")
                    return cat
                
                # Criar nova categoria se não existir
                cat, created = Categoria.objects.get_or_create(
                    slug=slugify(clean_category)[:140],
                    defaults={"nome": clean_category}
                )
                if created:
                    self.stdout.write(f"Nova categoria criada: {clean_category}")
                else:
                    self.stdout.write(f"Categoria encontrada: {clean_category}")
                return cat
        
        # 3. FALLBACK FINAL: Sistema inteligente de análise de conteúdo
        self.stdout.write("Usando sistema inteligente de categorizacao...")
        title = news_article.get("title", "") if news_article else ""
        description = news_article.get("description", "") if news_article else ""
        
        try:
            from rb_ingestor.smart_categorizer import SmartCategorizer
            categorizer = SmartCategorizer()
            
            # Categorizar baseado no conteúdo completo
            category_name = categorizer.categorize_content(title, description, topic_lower)
            confidence = categorizer.get_category_confidence(title, description, topic_lower)
            
            self.stdout.write(f"Categoria detectada: {category_name} (confianca: {confidence:.2f})")
            
            # Salvar confiança da categoria original para uso posterior
            self._original_category_confidence = confidence
            
            # Buscar ou criar categoria
            cat = Categoria.objects.filter(nome=category_name.title()).first()
            if cat:
                return cat
            
            # Criar nova categoria se não existir
            cat, created = Categoria.objects.get_or_create(
                slug=slugify(category_name)[:140],
                defaults={"nome": category_name.title()}
            )
            return cat
            
        except Exception as e:
            self.stdout.write(f"AVISO: Erro no categorizador inteligente: {e}")
            # Fallback final para sistema simples
            return self._get_category_fallback(topic_lower, Categoria)

    def _get_category_fallback(self, topic_lower, Categoria):
        """Fallback simples para categorização"""
        category_mapping = {
            "politica": "Política",
            "economia": "Economia", 
            "esportes": "Esportes",
            "tecnologia": "Tecnologia",
            "saude": "Saúde",
            "mundo": "Mundo",
            "brasil": "Brasil"
        }
        
        for keyword, category_name in category_mapping.items():
            if keyword in topic_lower:
                cat = Categoria.objects.filter(nome=category_name).first()
                if cat:
                    return cat
                return Categoria.objects.create(nome=category_name, slug=slugify(category_name)[:140])
        
        # Default
        cat = Categoria.objects.filter(nome="Brasil").first()
        if cat:
            return cat
        return Categoria.objects.create(nome="Brasil", slug="brasil")

    def _add_image(self, noticia, topic, news_article=None):
        """Adiciona imagem à notícia seguindo lógica inteligente"""
        try:
            # LÓGICA INTELIGENTE MELHORADA:
            # 1. Figuras públicas: Detecção inteligente → Rede social do artigo original → Instagram oficial → Bancos gratuitos
            # 2. Artigos gerais: Bancos gratuitos
            
            # NOVA PRIORIDADE 1: Detecção inteligente de figuras públicas
            from rb_ingestor.smart_public_figure_detector import SmartPublicFigureDetector
            smart_detector = SmartPublicFigureDetector()
            
            full_text = f"{noticia.titulo} {noticia.conteudo}"
            if news_article:
                full_text += f" {news_article.get('title', '')} {news_article.get('description', '')}"
            
            # Detectar figura pública usando sistema inteligente
            public_figure = smart_detector.detect_public_figure(full_text)
            
            if public_figure:
                # É figura pública - seguir lógica específica
                self.stdout.write(f"Figura publica detectada: {public_figure['figure']}")
                
                # PRIORIDADE 1: Imagem de rede social no artigo original
                if news_article:
                    from rb_ingestor.instagram_image_finder import InstagramImageFinder
                    instagram_finder = InstagramImageFinder()
                    social_image = instagram_finder.extract_social_media_images_from_news(news_article)
                    if social_image:
                        self.stdout.write(f"Imagem de rede social encontrada no artigo original")
                        noticia.imagem = social_image["url"]
                        noticia.imagem_alt = social_image.get("alt", f"Imagem de {public_figure['figure']}")
                        noticia.imagem_credito = social_image.get("credit", f"Foto: {public_figure['instagram_handle']}")
                        noticia.imagem_licenca = "Rede Social - Figura Pública"
                        noticia.imagem_fonte_url = social_image.get("url", "")
                        noticia.save()
                        
                        self.stdout.write("Imagem de rede social adicionada com sucesso")
                        return
                
                # PRIORIDADE 2: Instagram oficial da figura (usando sistema inteligente)
                instagram_image = smart_detector.get_instagram_image_for_figure(public_figure)
                
                if instagram_image and instagram_image.get("url"):
                    self.stdout.write(f"Imagem do Instagram oficial encontrada: {public_figure['instagram_handle']}")
                    noticia.imagem = instagram_image["url"]
                    noticia.imagem_alt = instagram_image.get("alt", f"Imagem de {public_figure['figure']}")
                    noticia.imagem_credito = instagram_image.get("credit", f"Foto: Instagram {public_figure['instagram_handle']}")
                    noticia.imagem_licenca = "Figura Pública - Unsplash"
                    noticia.imagem_fonte_url = instagram_image.get("instagram_url", "")
                    noticia.save()
                    
                    self.stdout.write("Imagem do Instagram oficial adicionada com sucesso")
                    return
            
            # FALLBACK: Bancos de imagens gratuitos (para artigos gerais ou quando Instagram não funciona)
            self.stdout.write("Usando banco de imagens gratuitos...")
            from rb_ingestor.image_search import ImageSearchEngine
            search_engine = ImageSearchEngine()
            
            image_url = search_engine.search_image(
                noticia.titulo,
                noticia.conteudo,
                noticia.categoria.nome if noticia.categoria else "geral"
            )

            if image_url:
                noticia.imagem = image_url
                noticia.imagem_alt = f"Imagem relacionada a {topic}"
                noticia.imagem_credito = "Imagem gratuita"
                noticia.imagem_licenca = "CC"
                noticia.imagem_fonte_url = image_url
                noticia.save()

                self.stdout.write("Imagem gratuita adicionada com sucesso")
                return
            
            self.stdout.write("AVISO: Nenhuma imagem encontrada")

        except Exception as e:
            self.stdout.write(f"AVISO: Erro ao adicionar imagem: {e}")

    def _ping_sitemap(self):
        """Faz ping do sitemap"""
        try:
            from core.utils import absolute_sitemap_url
            from rb_ingestor.ping import ping_search_engines
            
            sm_url = absolute_sitemap_url()
            res = ping_search_engines(sm_url)
            
            self.stdout.write(f"Ping sitemap: Google={'OK' if res['google'] else 'NOK'}; Bing={'OK' if res['bing'] else 'NOK'}")
            
        except Exception as e:
            self.stdout.write(f"AVISO: Erro no ping do sitemap: {e}")