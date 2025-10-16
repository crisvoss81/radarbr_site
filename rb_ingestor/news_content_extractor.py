# rb_ingestor/news_content_extractor.py
"""
Extrator de conteúdo real de notícias
"""
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, urljoin
from typing import Optional, Dict
import time
from contextlib import contextmanager

class NewsContentExtractor:
    """Extrai conteúdo real de notícias acessando URLs diretamente"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    # ===== NOVA API SIMPLIFICADA =====
    def get_rss_items_for_topic(self, topic: str, max_items: int = 5) -> list:
        """Busca itens de RSS do Google News para um tópico."""
        try:
            import urllib.parse
            import xml.etree.ElementTree as ET
            q = urllib.parse.quote_plus(topic)
            rss_url = f"https://news.google.com/rss/search?q={q}&hl=pt-BR&gl=BR&ceid=BR:pt-BR"
            resp = self.session.get(rss_url, timeout=15)
            if resp.status_code != 200 or not resp.text.strip():
                return []
            root = ET.fromstring(resp.text)
            channel = root.find('channel')
            items = []
            if channel is not None:
                for item in channel.findall('item')[:max_items]:
                    title_el = item.find('title')
                    link_el = item.find('link')
                    desc_el = item.find('description')
                    items.append({
                        'title': title_el.text if title_el is not None else '',
                        'link': link_el.text if link_el is not None else '',
                        'description': desc_el.text if desc_el is not None else ''
                    })
            return items
        except Exception as e:
            print(f"⚠ Falha RSS tópico: {e}")
            return []

    def extract_from_google_news_link(self, gnews_link: str) -> Optional[Dict]:
        """Abre link do Google News no navegador e extrai conteúdo da página final do publisher.
        Sistema de fallback: tenta até 3 links externos do cluster em ordem.
        """
        final_url, html = self._get_final_url_and_html_with_browser(gnews_link)
        
        # Se ainda estamos no Google News, tentar extrair links externos e abrir cada um
        if (not final_url or 'news.google.com' in final_url) and html:
            links = self._find_external_links_from_google_html(html, gnews_link)
            print(f"🔗 Links externos do cluster encontrados: {len(links)}")
            
            # Tentar até 3 links externos (margem de segurança)
            for idx, ext_link in enumerate(links[:3], start=1):
                try:
                    print(f"➡ Tentando link externo #{idx}: {ext_link[:60]}...")
                    u2, h2 = self._get_final_url_and_html_with_browser(ext_link)
                    
                    if u2 and h2 and 'news.google.com' not in u2:
                        final_url, html = u2, h2
                        print(f"✅ Sucesso no link externo #{idx}: {u2[:60]}...")
                        break
                    else:
                        print(f"⚠ Link externo #{idx} ainda redireciona para Google News")
                        
                except Exception as e:
                    print(f"❌ Erro no link externo #{idx}: {e}")
                    continue
        
        # Verificar se conseguimos sair do Google News
        if not final_url or 'news.google.com' in final_url or not html:
            print("❌ Não foi possível acessar conteúdo do publisher")
            return None
        
        # Extrair dados da página final
        soup = BeautifulSoup(html, 'html.parser')
        extracted_data = {
            'url': final_url,
            'title': self._extract_title(soup),
            'description': self._extract_description(soup),
            'content': self._extract_main_content(soup),
            'category': self._extract_category(soup),
            'inferred_category': self._infer_category_from_url(final_url),
            'author': self._extract_author(soup),
            'date': self._extract_date(soup),
            'images': self._extract_images(soup),
            'source_domain': self._extract_domain(final_url)
        }
        
        # Validar qualidade do conteúdo extraído
        if extracted_data['title'] and extracted_data['content'] and len(extracted_data['content']) > 100:
            print(f"✅ Conteúdo (publisher) extraído: {len(extracted_data['content'])} chars")
            print(f"✅ Site original: {extracted_data['source_domain']}")
            return extracted_data
        
        print("❌ Conteúdo extraído insuficiente ou inválido")
        return None

    def extract_best_for_topic(self, topic: str, max_items: int = 6) -> Optional[Dict]:
        """Tenta os primeiros itens do RSS abrindo em navegador até conseguir o artigo original (com retry e fallback)."""
        items = self.get_rss_items_for_topic(topic, max_items=max_items)
        print(f"🔎 RSS itens encontrados: {len(items)}")
        
        if not items:
            print("❌ Nenhum item RSS encontrado")
            return None
        
        # Tentar cada item com sistema de fallback
        for idx, item in enumerate(items, start=1):
            link = item.get('link')
            if not link:
                continue
            
            print(f"🧭 Tentando item #{idx}: {link[:80]}...")
            
            # Tentar extrair conteúdo com retry
            data = self._extract_with_retry(link, max_attempts=2)
            if data:
                print(f"✅ Sucesso no item #{idx}")
                return data
            
            print(f"❌ Falha no item #{idx}, tentando próximo...")
        
        print("❌ Todos os itens falharam na extração")
        return None
    
    def _extract_with_retry(self, link: str, max_attempts: int = 2) -> Optional[Dict]:
        """Extrai conteúdo com retry e sistema de fallback."""
        for attempt in range(1, max_attempts + 1):
            try:
                print(f"🔄 Tentativa {attempt}/{max_attempts}")
                data = self.extract_from_google_news_link(link)
                
                if data and data.get('content') and len(data['content']) > 200:
                    print(f"✅ Conteúdo extraído: {len(data['content'])} chars")
                    return data
                
                print(f"⚠ Tentativa {attempt} falhou ou conteúdo insuficiente")
                
                if attempt < max_attempts:
                    print("⏳ Aguardando 3s antes do retry...")
                    time.sleep(3)
                    
            except Exception as e:
                print(f"❌ Erro na tentativa {attempt}: {e}")
                if attempt < max_attempts:
                    print("⏳ Aguardando 3s antes do retry...")
                    time.sleep(3)
        
        return None

    # ===== API ANTIGA (mantida para compatibilidade interna) =====
    def extract_content_from_url(self, url: str) -> Optional[Dict]:
        """Extrai conteúdo real de uma URL de notícia"""
        try:
            print(f"🌐 Acessando URL: {url[:100]}...")
            
            # Para links do Google News: abrir diretamente no navegador headless e usar a página final
            if 'news.google.com' in url:
                data = self.extract_from_google_news_link(url)
                return data
            
            # Fazer requisição direta
            response = self.session.get(url, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            # Parse do HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extrair dados da notícia
            extracted_data = {
                'url': url,
                'title': self._extract_title(soup),
                'description': self._extract_description(soup),
                'content': self._extract_main_content(soup),
                'category': self._extract_category(soup),
                'inferred_category': self._infer_category_from_url(url),
                'author': self._extract_author(soup),
                'date': self._extract_date(soup),
                'images': self._extract_images(soup),
                'source_domain': self._extract_domain(url)
            }
            
            # Verificar se conseguiu extrair conteúdo válido
            if extracted_data['title'] and extracted_data['content']:
                print(f"✅ Conteúdo extraído: {len(extracted_data['content'])} caracteres")
                return extracted_data
            else:
                print("⚠ Conteúdo insuficiente extraído")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao acessar URL: {e}")
            return None

    def _resolve_with_browser(self, url: str) -> Optional[str]:
        """[DEPRECATED] Mantido por compatibilidade: use _get_final_url_and_html_with_browser."""
        try:
            from playwright.sync_api import sync_playwright
            print("🧭 Abrindo link no navegador headless para resolver destino...")
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(user_agent=self.session.headers.get('User-Agent'))
                page = context.new_page()
                page.goto(url, timeout=30000, wait_until='load')
                # Esperar possíveis redirecionamentos dinâmicos
                page.wait_for_timeout(1500)
                final_url = page.url
                context.close()
                browser.close()
                if final_url and 'news.google.com' not in final_url:
                    print(f"➡ URL final via navegador: {final_url}")
                    return final_url
        except Exception as e:
            print(f"⚠ Falha ao resolver com navegador: {e}")
        return None

    def _get_final_url_and_html_with_browser(self, url: str) -> (Optional[str], Optional[str]):
        """Abre o link no Chromium headless, retorna URL final e HTML renderizado."""
        try:
            from playwright.sync_api import sync_playwright
            print("🧭 Abrindo link no navegador headless...")
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(user_agent=self.session.headers.get('User-Agent'))
                page = context.new_page()
                # Estratégia multi-fase de carregamento
                for wait_state in ['domcontentloaded', 'load', 'networkidle']:
                    try:
                        page.goto(url, timeout=60000, wait_until=wait_state)
                        break
                    except Exception as _:
                        if wait_state == 'networkidle':
                            raise
                        continue
                # Esperar elementos típicos de artigo
                try:
                    page.wait_for_selector('article, main, [itemprop="articleBody"], .post-content, .entry-content, .article-body, .news-content', timeout=7000)
                except Exception:
                    pass
                # Scroll para carregar lazy content
                try:
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(1500)
                    page.evaluate("window.scrollTo(0, 0)")
                except Exception:
                    pass
                # Tentar clicar banners de consentimento comuns
                try:
                    selectors = [
                        'text=Aceitar', 'text=Concordo', 'text=Accept', 'text=Accept all', 'text=I agree',
                        'button[aria-label="Aceitar tudo"]', 'button[aria-label="Accept all"]'
                    ]
                    for sel in selectors:
                        try:
                            btn = page.locator(sel)
                            if btn and btn.count() > 0:
                                btn.first.click(timeout=2000)
                                page.wait_for_timeout(1000)
                                break
                        except Exception:
                            continue
                except Exception:
                    pass
                page.wait_for_timeout(5000)
                final_url = page.url
                html = page.content()
                context.close()
                browser.close()
                print(f"➡ URL final: {final_url}")
                return final_url, html
        except Exception as e:
            print(f"⚠ Falha ao obter HTML via navegador: {e}")
        return None, None

    def _find_external_links_from_google_html(self, html: str, base_url: str) -> list:
        """Encontra links externos (publisher) no HTML do cluster do Google News em ordem de exibição."""
        links = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            for a in soup.find_all('a', href=True):
                href = a.get('href')
                if not href:
                    continue
                if href.startswith('./'):
                    href = urljoin(base_url, href)
                # Decodificar links do Google que encapsulam url=
                try:
                    parsed = urlparse(href)
                    if 'google.com' in parsed.netloc and ('url=' in parsed.query or parsed.path.startswith('/url')):
                        from urllib.parse import parse_qs
                        qs = parse_qs(parsed.query)
                        if 'url' in qs and qs['url']:
                            href = qs['url'][0]
                except Exception:
                    pass
                # Filtrar links externos reais
                if href.startswith('http') and 'news.google.com' not in href and 'google.com' not in href:
                    # Evitar duplicados preservando ordem
                    if href not in links:
                        links.append(href)
        except Exception as e:
            print(f"⚠ Erro ao extrair links externos do cluster: {e}")
        return links

    def _extract_publisher_url_from_google_html(self, html: str, base_url: str) -> Optional[str]:
        """Tenta extrair a URL do publisher do HTML de uma página do Google News."""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            # 1) Meta refresh
            meta_refresh = soup.find('meta', attrs={'http-equiv': re.compile('refresh', re.I)})
            if meta_refresh and meta_refresh.get('content'):
                content = meta_refresh.get('content')
                m = re.search(r'url=([^;]+)$', content, re.I)
                if m:
                    href = m.group(1).strip().strip('"').strip("'")
                    if href.startswith('./'):
                        href = urljoin(base_url, href)
                    if href.startswith('http') and 'news.google.com' not in href:
                        return href

            # 2) Link canonical
            link_canonical = soup.find('link', rel=lambda x: x and 'canonical' in x)
            if link_canonical and link_canonical.get('href'):
                href = link_canonical.get('href')
                if href.startswith('http') and 'news.google.com' not in href:
                    return href

            # 3) Primeiro link externo http(s)
            for a in soup.find_all('a', href=True):
                href = a.get('href')
                if href.startswith('./'):
                    href = urljoin(base_url, href)
                if href.startswith('http') and 'news.google.com' not in href and 'google.com' not in href:
                    return href
        except Exception as e:
            print(f"⚠ Erro ao extrair publisher URL do HTML: {e}")
        return None
    
    def _extract_from_google_news(self, google_url: str) -> Optional[Dict]:
        """Extrai conteúdo de sites originais mencionados no Google News"""
        try:
            print("🔍 Analisando Google News para encontrar sites originais...")
            
            # Tentativa 0: seguir redirecionamentos do link para chegar ao publisher
            try:
                follow = self.session.get(google_url, timeout=15, allow_redirects=True)
                final_url = follow.url
                if final_url and 'news.google.com' not in final_url:
                    print(f"➡ Redirecionado para: {final_url}")
                    # Extrair diretamente do destino
                    soup_final = BeautifulSoup(follow.content, 'html.parser')
                    extracted_data = {
                        'url': final_url,
                        'title': self._extract_title(soup_final),
                        'description': self._extract_description(soup_final),
                        'content': self._extract_main_content(soup_final),
                        'author': self._extract_author(soup_final),
                        'date': self._extract_date(soup_final),
                        'images': self._extract_images(soup_final),
                        'source_domain': self._extract_domain(final_url)
                    }
                    if extracted_data['title'] and extracted_data['content'] and len(extracted_data['content']) > 200:
                        print(f"✅ Conteúdo extraído via redirect: {len(extracted_data['content'])} caracteres")
                        return extracted_data
            except Exception as e:
                print(f"⚠ Falha no redirect inicial: {e}")

            # Acessar página do Google News
            response = self.session.get(google_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 1) Procurar por links externos diretos dentro da página do Google News
            external_links = []
            for a in soup.find_all('a', href=True):
                href = a.get('href')
                if not href:
                    continue
                # Normalizar URLs relativas que às vezes aparecem como ./articles/...
                if href.startswith('./'):
                    href = urljoin(google_url, href)
                
                # Extrair links externos encapsulados em google.com/url?url=
                try:
                    parsed = urlparse(href)
                    if 'google.com' in parsed.netloc and ('url=' in parsed.query or parsed.path.startswith('/url')):
                        from urllib.parse import parse_qs
                        qs = parse_qs(parsed.query)
                        if 'url' in qs and qs['url']:
                            href = qs['url'][0]
                except Exception:
                    pass

                # Ignorar links do próprio Google News após tentar extrair url= acima
                if 'news.google.com' in href:
                    continue
                
                # Aceitar apenas http(s)
                if not href.startswith('http'):
                    continue
                
                external_links.append(href)
            
            # Remover duplicados preservando ordem
            seen = set()
            unique_external_links = []
            for link in external_links:
                if link not in seen:
                    unique_external_links.append(link)
                    seen.add(link)
            
            # Tentar abrir os primeiros links externos que pareçam notícia
            for link in unique_external_links[:8]:
                try:
                    if not self._looks_like_news_url(link):
                        continue
                    print(f"🧭 Testando link externo: {link}")
                    news_response = self.session.get(link, timeout=15)
                    news_response.raise_for_status()
                    news_soup = BeautifulSoup(news_response.content, 'html.parser')
                    extracted_data = {
                        'url': link,
                        'title': self._extract_title(news_soup),
                        'description': self._extract_description(news_soup),
                        'content': self._extract_main_content(news_soup),
                        'author': self._extract_author(news_soup),
                        'date': self._extract_date(news_soup),
                        'images': self._extract_images(news_soup),
                        'source_domain': self._extract_domain(link)
                    }
                    if extracted_data['title'] and extracted_data['content'] and len(extracted_data['content']) > 200:
                        print(f"✅ Conteúdo extraído do link externo: {len(extracted_data['content'])} caracteres")
                        return extracted_data
                except Exception as e:
                    print(f"⚠ Erro ao acessar link externo {link}: {e}")
                    continue
            
            # 2) Se não achou link externo direto, cair no método baseado em sites conhecidos
            # Extrair texto da página para encontrar nomes de sites
            page_text = soup.get_text()
            
            # Procurar por nomes de sites conhecidos no texto
            known_sites = [
                'metropoles.com',
                'terra.com.br', 
                'g1.globo.com',
                'oglobo.globo.com',
                'folha.uol.com.br',
                'estadao.com.br',
                'uol.com.br',
                'r7.com',
                'ig.com.br',
                'exame.com',
                'jornalcorreio.com.br'
            ]
            
            found_sites = []
            for site in known_sites:
                if site in page_text.lower():
                    found_sites.append(site)
            
            # Se encontrou sites, tentar acessá-los diretamente
            if found_sites:
                print(f"🎯 Sites encontrados: {', '.join(found_sites)}")
                
                # Tentar acessar cada site encontrado
                for site in found_sites:
                    try:
                        # Construir URL de busca no site
                        search_urls = [
                            f"https://{site}/busca",
                            f"https://{site}/search",
                            f"https://{site}/noticias"
                        ]
                        
                        for search_url in search_urls:
                            try:
                                print(f"🌐 Tentando acessar: {search_url}")
                                
                                response = self.session.get(search_url, timeout=10)
                                if response.status_code == 200:
                                    soup = BeautifulSoup(response.content, 'html.parser')
                                    
                                    # Procurar por links de notícias recentes
                                    news_links = self._find_recent_news_links(soup, site)
                                    
                                    if news_links:
                                        # Tentar acessar a primeira notícia encontrada
                                        for news_url in news_links[:2]:
                                            try:
                                                print(f"📰 Acessando notícia: {news_url}")
                                                
                                                news_response = self.session.get(news_url, timeout=15)
                                                news_response.raise_for_status()
                                                
                                                news_soup = BeautifulSoup(news_response.content, 'html.parser')
                                                
                                                # Extrair dados da notícia
                                                extracted_data = {
                                                    'url': news_url,
                                                    'title': self._extract_title(news_soup),
                                                    'description': self._extract_description(news_soup),
                                                    'content': self._extract_main_content(news_soup),
                                                    'author': self._extract_author(news_soup),
                                                    'date': self._extract_date(news_soup),
                                                    'images': self._extract_images(news_soup),
                                                    'source_domain': self._extract_domain(news_url)
                                                }
                                                
                                                # Verificar se conseguiu extrair conteúdo válido
                                                if extracted_data['title'] and extracted_data['content'] and len(extracted_data['content']) > 200:
                                                    print(f"✅ Conteúdo extraído do site original: {len(extracted_data['content'])} caracteres")
                                                    return extracted_data
                                                
                                            except Exception as e:
                                                print(f"⚠ Erro ao acessar notícia {news_url}: {e}")
                                                continue
                                
                            except Exception as e:
                                print(f"⚠ Erro ao acessar {search_url}: {e}")
                                continue
                    
                    except Exception as e:
                        print(f"⚠ Erro ao processar site {site}: {e}")
                        continue
            
            print("❌ Não foi possível acessar nenhum site original")
            return None
            
        except Exception as e:
            print(f"❌ Erro ao analisar Google News: {e}")
            return None

    def find_original_url_by_title_and_source(self, title: str, source_name: str) -> Optional[str]:
        """Tenta encontrar a URL original pesquisando por título dentro do domínio da fonte."""
        try:
            if not title or not source_name:
                # Se não houver fonte, tentar busca geral pelo título
                return self._search_web_for_title(title)
            # Mapear nomes de fontes comuns para domínios
            source_to_domain = {
                'G1': 'g1.globo.com',
                'O Globo': 'oglobo.globo.com',
                'Folha': 'folha.uol.com.br',
                'Folha de S.Paulo': 'folha.uol.com.br',
                'Estadão': 'estadao.com.br',
                'UOL': 'uol.com.br',
                'Terra': 'terra.com.br',
                'R7': 'r7.com',
                'IG': 'ig.com.br',
                'Metrópoles': 'metropoles.com',
                'G1 - Globo': 'g1.globo.com',
                'G1 - O Globo': 'g1.globo.com',
                'G1 - Portal G1': 'g1.globo.com',
                'G1 - Globo.com': 'g1.globo.com',
            }
            domain = source_to_domain.get(source_name.strip(), '')
            if not domain:
                # tentar derivar domínio simples do nome
                domain = source_name.lower().replace(' ', '') + '.com.br'

            query = f"site:{domain} {title}"
            print(f"🔎 Buscando URL original por título e domínio: {query}")

            # Usar DuckDuckGo HTML
            search_url = 'https://duckduckgo.com/html/'
            params = {'q': query}
            resp = self.session.post(search_url, data=params, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, 'html.parser')
                for a in soup.select('a.result__a, a.result__url'):
                    href = a.get('href')
                    if href and domain in href and href.startswith('http'):
                        print(f"✅ Encontrado via busca: {href}")
                        return href
            
            # Se não encontrou no domínio, tentar busca geral pelo título
            return self._search_web_for_title(title)
        except Exception as e:
            print(f"⚠ Erro na busca por título/domínio: {e}")
        return self._search_web_for_title(title)

    def _search_web_for_title(self, title: str) -> Optional[str]:
        """Busca geral pelo título e retorna um link que pareça notícia."""
        try:
            if not title:
                return None
            query = title.strip()
            print(f"🔎 Busca geral por título: {query}")
            search_url = 'https://duckduckgo.com/html/'
            params = {'q': query}
            resp = self.session.get(search_url, params=params, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, 'html.parser')
                for a in soup.select('a.result__a, a.result__url'):
                    href = a.get('href')
                    if href and href.startswith('http') and self._looks_like_news_url(href):
                        print(f"✅ Encontrado via busca geral: {href}")
                        return href
            # Fallback: Bing
            bing_url = 'https://www.bing.com/search'
            resp2 = self.session.get(bing_url, params={'q': query}, timeout=15)
            if resp2.status_code == 200:
                soup2 = BeautifulSoup(resp2.content, 'html.parser')
                for a in soup2.select('li.b_algo h2 a, a[href]'):
                    href = a.get('href')
                    if href and href.startswith('http') and self._looks_like_news_url(href):
                        print(f"✅ Encontrado via Bing: {href}")
                        return href
        except Exception as e:
            print(f"⚠ Erro na busca geral: {e}")
        return None
    
    def _find_recent_news_links(self, soup: BeautifulSoup, site: str) -> list:
        """Encontra links de notícias recentes em um site"""
        links = []
        
        # Procurar por links que parecem ser notícias
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link.get('href')
            if href:
                # Converter URL relativa em absoluta
                if href.startswith('/'):
                    href = f"https://{site}{href}"
                elif href.startswith('//'):
                    href = f"https:{href}"
                
                # Verificar se parece ser um link de notícia
                if self._looks_like_news_url(href):
                    links.append(href)
        
        return links[:5]  # Retornar até 5 links
    
    def _is_google_news_url(self, url: str) -> bool:
        """Verifica se o URL é do Google News"""
        if not url:
            return False
        
        google_news_domains = [
            'news.google.com',
            'news.google.com.br',
            'news.google.co.uk'
        ]
        
        parsed = urlparse(url)
        return parsed.netloc.lower() in google_news_domains
    
    def _looks_like_news_url(self, url: str) -> bool:
        """Verifica se o URL parece ser de uma notícia"""
        if not url:
            return False
        
        # Domínios conhecidos de notícias brasileiras
        news_domains = [
            'g1.globo.com',
            'oglobo.globo.com',
            'folha.uol.com.br',
            'estadao.com.br',
            'uol.com.br',
            'r7.com',
            'terra.com.br',
            'ig.com.br',
            'exame.com',
            'valor.com.br',
            'correio24horas.com.br',
            'bahia.ba',
            'ibahia.com',
            'atarde.com.br',
            'tribunadabahia.com.br',
            'metropoles.com',
            'jornalcorreio.com.br'
        ]
        
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Verificar se é um domínio de notícia conhecido
        for news_domain in news_domains:
            if domain == news_domain or domain.endswith('.' + news_domain):
                return True
        
        # Verificar padrões comuns de URLs de notícias
        news_patterns = [
            r'/\d{4}/\d{2}/\d{2}/',  # Data no formato YYYY/MM/DD
            r'/noticia/',             # Contém "noticia"
            r'/materia/',             # Contém "materia"
            r'/artigo/',              # Contém "artigo"
            r'\.html$',               # Termina com .html
            r'\.php$',                # Termina com .php
        ]
        
        for pattern in news_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        
        return False
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extrai o título da notícia"""
        # Procurar por meta tags primeiro
        meta_title = soup.find('meta', property='og:title')
        if meta_title and meta_title.get('content'):
            return meta_title.get('content').strip()
        
        meta_title = soup.find('meta', attrs={'name': 'title'})
        if meta_title and meta_title.get('content'):
            return meta_title.get('content').strip()
        
        # Procurar por elementos de título
        title_selectors = [
            'h1',
            '.titulo',
            '.title',
            '.headline',
            '.noticia-titulo',
            '.materia-titulo',
            '.artigo-titulo',
            '.post-title',
            '.entry-title',
            '[data-testid="headline"]',
            '.content-head__title'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text().strip()
                if title and len(title) > 10:  # Título deve ter pelo menos 10 caracteres
                    return title
        
        return ''
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extrai a descrição/resumo da notícia"""
        # Procurar por meta tags
        meta_desc = soup.find('meta', property='og:description')
        if meta_desc and meta_desc.get('content'):
            return meta_desc.get('content').strip()
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc.get('content').strip()
        
        # Procurar por subtítulo ou resumo
        desc_selectors = [
            '.subtitulo',
            '.resumo',
            '.lead',
            '.summary',
            '.noticia-resumo',
            '.materia-resumo',
            '.artigo-resumo',
            '.post-excerpt',
            '.entry-summary',
            '.content-head__subtitle'
        ]
        
        for selector in desc_selectors:
            element = soup.select_one(selector)
            if element:
                desc = element.get_text().strip()
                if desc and len(desc) > 20:  # Descrição deve ter pelo menos 20 caracteres
                    return desc
        
        return ''
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extrai o conteúdo principal da notícia"""
        # Remover elementos indesejados
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
            element.decompose()
        
        # Procurar por conteúdo principal
        content_selectors = [
            '.conteudo',
            '.noticia-conteudo',
            '.materia-conteudo',
            '.artigo-conteudo',
            '.texto',
            '.content',
            'article',
            '.post-content',
            '.entry-content',
            '.article-body',
            '.story-body',
            '.news-content',
            '[data-testid="article-body"]',
            '[itemprop="articleBody"]',
            'main',
            '.post-content__body',
            '.single-content',
            '.c-entry-content',
            '.sg-text',
            '.article__content',
            '.article-content'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                # Limpar conteúdo
                content = self._clean_content(element)
                if content and len(content) > 100:  # Conteúdo deve ter pelo menos 100 caracteres
                    return content
        
        # Fallback: procurar por parágrafos
        paragraphs = soup.find_all('p')
        if paragraphs:
            content_parts = []
            for p in paragraphs:
                text = p.get_text().strip()
                if text and len(text) > 20:  # Parágrafo deve ter pelo menos 20 caracteres
                    content_parts.append(text)
            
            if content_parts:
                return '\n\n'.join(content_parts)
        
        return ''
    
    def _clean_content(self, element) -> str:
        """Limpa o conteúdo extraído"""
        # Remover elementos indesejados dentro do conteúdo
        for unwanted in element(['script', 'style', 'nav', 'advertisement', 'ad', '.ad']):
            unwanted.decompose()
        
        # Extrair texto
        text = element.get_text()
        
        # Limpar texto
        text = re.sub(r'\s+', ' ', text)  # Múltiplos espaços em um
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Múltiplas quebras de linha
        
        return text.strip()
    
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """Extrai o autor da notícia"""
        author_selectors = [
            '.autor',
            '.author',
            '.byline',
            '.escritor',
            '.writer',
            '[data-testid="author"]',
            '.content-head__author'
        ]
        
        for selector in author_selectors:
            element = soup.select_one(selector)
            if element:
                author = element.get_text().strip()
                if author:
                    return author
        
        return ''
    
    def _extract_date(self, soup: BeautifulSoup) -> str:
        """Extrai a data da notícia"""
        date_selectors = [
            '.data',
            '.date',
            '.published',
            '.timestamp',
            'time',
            '[data-testid="timestamp"]',
            '.content-head__date'
        ]
        
        for selector in date_selectors:
            element = soup.select_one(selector)
            if element:
                date = element.get_text().strip()
                if date:
                    return date
        
        return ''
    
    def _extract_images(self, soup: BeautifulSoup) -> list:
        """Extrai imagens da notícia"""
        images = []
        
        # Procurar por imagens
        img_elements = soup.find_all('img')
        for img in img_elements:
            src = img.get('src') or img.get('data-src')
            if src:
                # Converter URL relativa em absoluta
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    # Precisa do domínio base
                    pass
                
                alt = img.get('alt', '')
                images.append({
                    'src': src,
                    'alt': alt
                })
        
        return images[:5]  # Máximo 5 imagens
    
    def _extract_category(self, soup: BeautifulSoup) -> str:
        """Tenta extrair a categoria da página do publisher."""
        # Meta tags comuns
        meta_sec = soup.find('meta', attrs={'property': 'article:section'})
        if meta_sec and meta_sec.get('content'):
            return meta_sec.get('content').strip()
        meta_sec = soup.find('meta', attrs={'name': 'section'})
        if meta_sec and meta_sec.get('content'):
            return meta_sec.get('content').strip()
        # Breadcrumbs
        breadcrumb_selectors = [
            '.breadcrumb a', '.breadcrumbs a', 'nav.breadcrumb a',
            'ol.breadcrumb li a', 'ul.breadcrumb li a'
        ]
        for sel in breadcrumb_selectors:
            el = soup.select(sel)
            if el:
                # último ou penúltimo item frequentemente é a seção
                text = el[-1].get_text().strip()
                if text and len(text) > 2:
                    return text
        # Labels/Tags
        tag_selectors = ['.tags a', '.label a', '.categoria a', '.category a']
        for sel in tag_selectors:
            el = soup.select_one(sel)
            if el:
                text = el.get_text().strip()
                if text:
                    return text
        return ''

    def _infer_category_from_url(self, url: str) -> str:
        """Heurística neutra para inferir categoria a partir da URL (sem favorecer uma específica)."""
        try:
            path = urlparse(url).path.lower()
            hints = [
                ('/politica', 'política'),
                ('/poder', 'política'),
                ('/economia', 'economia'),
                ('/mercados', 'economia'),
                ('/mundo', 'mundo'),
                ('/internacional', 'mundo'),
                ('/esporte', 'esportes'),
                ('/esportes', 'esportes'),
                ('/tecnologia', 'tecnologia'),
                ('/ciencia', 'ciência'),
                ('/saude', 'saúde'),
                ('/brasil', 'brasil'),
                ('/educacao', 'educação')
            ]
            for fragment, cat in hints:
                if fragment in path:
                    return cat
        except Exception:
            pass
        return ''
    
    def _extract_domain(self, url: str) -> str:
        """Extrai o domínio da URL"""
        parsed = urlparse(url)
        return parsed.netloc.lower()
    
    def stdout_write(self, message: str):
        """Método para compatibilidade com Django management commands"""
        print(message)
