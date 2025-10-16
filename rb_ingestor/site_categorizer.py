# rb_ingestor/site_categorizer.py
"""
Sistema para extrair categorias dos sites de origem das notícias
"""
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import time
from django.conf import settings

class SiteCategorizer:
    """Extrai categorias dos sites de origem das notícias"""
    
    def __init__(self):
        # Mapeamento de sites conhecidos e seus seletores CSS
        self.site_selectors = {
            'g1.globo.com': {
                'category_selectors': [
                    '.header-editoria',
                    '.editoria',
                    '.breadcrumb a',
                    '.menu-editoria a',
                    '[data-testid="editoria"]'
                ],
                'fallback_keywords': ['g1', 'globo']
            },
            'oglobo.globo.com': {
                'category_selectors': [
                    '.editoria',
                    '.breadcrumb a',
                    '.menu-editoria a'
                ],
                'fallback_keywords': ['oglobo', 'globo']
            },
            'folha.uol.com.br': {
                'category_selectors': [
                    '.breadcrumb a',
                    '.editoria',
                    '.menu-editoria a'
                ],
                'fallback_keywords': ['folha', 'uol']
            },
            'estadao.com.br': {
                'category_selectors': [
                    '.breadcrumb a',
                    '.editoria',
                    '.menu-editoria a'
                ],
                'fallback_keywords': ['estadão', 'estadao']
            },
            'cnnbrasil.com.br': {
                'category_selectors': [
                    '.breadcrumb a',
                    '.editoria',
                    '.menu-editoria a'
                ],
                'fallback_keywords': ['cnn', 'brasil']
            },
            'infomoney.com.br': {
                'category_selectors': [
                    '.breadcrumb a',
                    '.editoria',
                    '.menu-editoria a'
                ],
                'fallback_keywords': ['infomoney', 'economia']
            },
            'forbes.com.br': {
                'category_selectors': [
                    '.breadcrumb a',
                    '.editoria',
                    '.menu-editoria a'
                ],
                'fallback_keywords': ['forbes', 'brasil']
            }
        }
        
        # Mapeamento de categorias comuns dos sites para nossas categorias
        self.category_mapping = {
            # Política
            'política': 'política',
            'politica': 'política',
            'governo': 'política',
            'eleições': 'política',
            'eleicoes': 'política',
            'congresso': 'política',
            'senado': 'política',
            'câmara': 'política',
            'camara': 'política',
            
            # Economia
            'economia': 'economia',
            'mercado': 'economia',
            'finanças': 'economia',
            'financas': 'economia',
            'negócios': 'economia',
            'negocios': 'economia',
            'dinheiro': 'economia',
            'investimentos': 'economia',
            
            # Esportes
            'esportes': 'esportes',
            'futebol': 'esportes',
            'olimpiadas': 'esportes',
            'olimpíadas': 'esportes',
            'copas': 'esportes',
            'mundial': 'esportes',
            
            # Tecnologia
            'tecnologia': 'tecnologia',
            'tech': 'tecnologia',
            'digital': 'tecnologia',
            'inovação': 'tecnologia',
            'inovacao': 'tecnologia',
            'startups': 'tecnologia',
            
            # Saúde
            'saúde': 'saúde',
            'saude': 'saúde',
            'medicina': 'saúde',
            'bem-estar': 'saúde',
            'bem estar': 'saúde',
            
            # Mundo
            'mundo': 'mundo',
            'internacional': 'mundo',
            'global': 'mundo',
            'exterior': 'mundo',
            
            # Brasil
            'brasil': 'brasil',
            'nacional': 'brasil',
            'sociedade': 'brasil',
            'cultura': 'brasil',
            'educação': 'brasil',
            'educacao': 'brasil'
        }
    
    def extract_category_from_url(self, url, timeout=10):
        """
        Extrai categoria do site de origem da notícia
        """
        try:
            # Parse da URL para identificar o domínio
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            
            # Remover www. se presente
            if domain.startswith('www.'):
                domain = domain[4:]
            
            print(f"🔍 Analisando site: {domain}")
            
            # Headers para simular navegador
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            # Fazer requisição
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            # Parse do HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Tentar extrair categoria usando seletores específicos do site
            category = self._extract_with_selectors(soup, domain)
            
            if category:
                return self._normalize_category(category)
            
            # Fallback: tentar extrair de breadcrumbs genéricos
            category = self._extract_from_breadcrumbs(soup)
            
            if category:
                return self._normalize_category(category)
            
            # Fallback: tentar extrair de meta tags
            category = self._extract_from_meta_tags(soup)
            
            if category:
                return self._normalize_category(category)
            
            return None
            
        except requests.exceptions.RequestException as e:
            self.stdout.write(f"⚠ Erro ao acessar {url}: {e}")
            return None
        except Exception as e:
            self.stdout.write(f"⚠ Erro ao processar {url}: {e}")
            return None
    
    def _extract_with_selectors(self, soup, domain):
        """Extrai categoria usando seletores específicos do site"""
        if domain in self.site_selectors:
            selectors = self.site_selectors[domain]['category_selectors']
            
            for selector in selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text().strip().lower()
                    if text and len(text) > 2 and len(text) < 50:
                        return text
        
        return None
    
    def _extract_from_breadcrumbs(self, soup):
        """Extrai categoria de breadcrumbs genéricos"""
        # Seletores comuns para breadcrumbs
        breadcrumb_selectors = [
            '.breadcrumb a',
            '.breadcrumbs a',
            '.breadcrumb li',
            '.breadcrumbs li',
            '[class*="breadcrumb"] a',
            '[class*="breadcrumb"] li'
        ]
        
        for selector in breadcrumb_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text().strip().lower()
                if text and len(text) > 2 and len(text) < 50:
                    # Pular elementos muito genéricos
                    if text not in ['home', 'início', 'inicio', 'notícias', 'noticias']:
                        return text
        
        return None
    
    def _extract_from_meta_tags(self, soup):
        """Extrai categoria de meta tags"""
        # Meta tags comuns para categorias
        meta_selectors = [
            'meta[property="article:section"]',
            'meta[name="category"]',
            'meta[name="section"]',
            'meta[property="og:section"]'
        ]
        
        for selector in meta_selectors:
            element = soup.select_one(selector)
            if element:
                content = element.get('content', '').strip().lower()
                if content and len(content) > 2 and len(content) < 50:
                    return content
        
        return None
    
    def _normalize_category(self, category):
        """Normaliza categoria extraída para nossas categorias"""
        category_lower = category.lower().strip()
        
        # Mapear para nossas categorias
        if category_lower in self.category_mapping:
            return self.category_mapping[category_lower]
        
        # Buscar por palavras-chave
        for our_category, keywords in {
            'política': ['política', 'politica', 'governo', 'eleições'],
            'economia': ['economia', 'mercado', 'finanças', 'negócios'],
            'esportes': ['esportes', 'futebol', 'olimpiadas'],
            'tecnologia': ['tecnologia', 'tech', 'digital', 'inovação'],
            'saúde': ['saúde', 'saude', 'medicina', 'bem-estar'],
            'mundo': ['mundo', 'internacional', 'global'],
            'brasil': ['brasil', 'nacional', 'sociedade']
        }.items():
            if any(keyword in category_lower for keyword in keywords):
                return our_category
        
        # Se não encontrar, retornar a categoria original capitalizada
        return category.title()
    
    def categorize_article(self, article):
        """
        Categoriza artigo baseado no site de origem
        """
        url = article.get('url', '')
        if not url:
            return None
        
        print(f"🌐 Extraindo categoria de: {url}")
        
        category = self.extract_category_from_url(url)
        
        if category:
            print(f"✅ Categoria extraída: {category}")
            return category
        else:
            print(f"⚠ Não foi possível extrair categoria")
            return None
