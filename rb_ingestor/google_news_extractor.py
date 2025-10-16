# rb_ingestor/google_news_extractor.py
"""
Extrator de URLs originais do Google News
"""
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
from typing import Optional, Dict

class GoogleNewsExtractor:
    """Extrai URLs originais das notícias do Google News"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def extract_original_url(self, google_news_url: str) -> Optional[str]:
        """Extrai o URL original de uma notícia do Google News"""
        try:
            # Fazer requisição para o Google News
            response = self.session.get(google_news_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Procurar por links que levam ao site original
            # Google News geralmente tem um link "Ver notícia completa" ou similar
            original_links = []
            
            # Procurar por links com texto indicativo
            link_texts = [
                'ver notícia completa', 'ler mais', 'continue lendo', 
                'read more', 'continue reading', 'full article',
                'ver matéria completa', 'ler matéria'
            ]
            
            for text in link_texts:
                links = soup.find_all('a', string=re.compile(text, re.IGNORECASE))
                original_links.extend([link.get('href') for link in links if link.get('href')])
            
            # Procurar por links que não sejam do Google News
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href')
                if href and not self._is_google_news_url(href):
                    # Verificar se parece ser um link de notícia
                    if self._looks_like_news_url(href):
                        original_links.append(href)
            
            # Procurar por meta tags que podem conter o URL original
            meta_tags = soup.find_all('meta')
            for meta in meta_tags:
                if meta.get('property') == 'og:url' or meta.get('name') == 'original-url':
                    url = meta.get('content')
                    if url and not self._is_google_news_url(url):
                        original_links.append(url)
            
            # Retornar o primeiro URL válido encontrado
            for url in original_links:
                if url and self._is_valid_news_url(url):
                    return url
            
            return None
            
        except Exception as e:
            print(f"Erro ao extrair URL original: {e}")
            return None
    
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
            'tribunadabahia.com.br'
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
    
    def _is_valid_news_url(self, url: str) -> bool:
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
    
    def get_enhanced_news_data(self, google_news_url: str) -> Optional[Dict]:
        """Obtém dados aprimorados da notícia acessando o site original"""
        original_url = self.extract_original_url(google_news_url)
        
        if not original_url:
            return None
        
        try:
            # Acessar o site original
            response = self.session.get(original_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extrair dados da notícia
            title = self._extract_title(soup)
            description = self._extract_description(soup)
            content = self._extract_content(soup)
            
            return {
                'original_url': original_url,
                'title': title,
                'description': description,
                'content': content,
                'source': self._extract_source_domain(original_url)
            }
            
        except Exception as e:
            print(f"Erro ao acessar site original: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extrai o título da notícia"""
        # Procurar por meta tags
        meta_title = soup.find('meta', property='og:title')
        if meta_title:
            return meta_title.get('content', '').strip()
        
        # Procurar por título principal
        title_selectors = [
            'h1',
            '.titulo',
            '.title',
            '.headline',
            '.noticia-titulo',
            '.materia-titulo'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
        
        return ''
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extrai a descrição da notícia"""
        # Procurar por meta tags
        meta_desc = soup.find('meta', property='og:description')
        if meta_desc:
            return meta_desc.get('content', '').strip()
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            return meta_desc.get('content', '').strip()
        
        # Procurar por subtítulo ou resumo
        desc_selectors = [
            '.subtitulo',
            '.resumo',
            '.lead',
            '.summary',
            '.noticia-resumo'
        ]
        
        for selector in desc_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
        
        return ''
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extrai o conteúdo principal da notícia"""
        content_selectors = [
            '.conteudo',
            '.noticia-conteudo',
            '.materia-conteudo',
            '.artigo-conteudo',
            '.texto',
            '.content',
            'article',
            '.post-content'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                # Remover scripts e estilos
                for script in element(['script', 'style']):
                    script.decompose()
                
                return element.get_text().strip()
        
        return ''
    
    def _extract_source_domain(self, url: str) -> str:
        """Extrai o domínio da fonte"""
        parsed = urlparse(url)
        return parsed.netloc.lower()



