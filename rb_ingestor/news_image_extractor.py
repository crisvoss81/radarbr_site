# rb_ingestor/news_image_extractor.py
"""
Sistema para extrair imagens da notícia original
"""
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging

logger = logging.getLogger(__name__)

class NewsImageExtractor:
    """Sistema para extrair imagens da notícia original"""
    
    def __init__(self):
        # Seletores CSS para diferentes sites de notícias
        self.image_selectors = {
            'oglobo.globo.com': {
                'main_image': ['.article-image img', '.content-image img', '.article-photo img'],
                'gallery_images': ['.gallery-item img', '.photo-gallery img'],
                'fallback': ['img[src*="globo"]', 'img[alt*="foto"]']
            },
            'g1.globo.com': {
                'main_image': ['.content-photo img', '.article-image img'],
                'gallery_images': ['.gallery-item img'],
                'fallback': ['img[src*="globo"]']
            },
            'folha.uol.com.br': {
                'main_image': ['.image img', '.article-image img'],
                'gallery_images': ['.gallery-item img'],
                'fallback': ['img[src*="folha"]']
            },
            'estadao.com.br': {
                'main_image': ['.image img', '.article-photo img'],
                'gallery_images': ['.gallery-item img'],
                'fallback': ['img[src*="estadao"]']
            }
        }
    
    def extract_images_from_news(self, news_url: str, news_title: str = "") -> dict:
        """
        Extrai imagens da notícia original
        """
        try:
            # Parse da URL para identificar o site
            parsed_url = urlparse(news_url)
            domain = parsed_url.netloc.lower()
            
            # Remover www. se presente
            if domain.startswith('www.'):
                domain = domain[4:]
            
            logger.info(f"🔍 Extraindo imagens de: {domain}")
            
            # Headers para simular navegador
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            }
            
            # Fazer requisição
            response = requests.get(news_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse do HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extrair imagens usando seletores específicos do site
            images = self._extract_images_with_selectors(soup, domain, news_url)
            
            if images:
                logger.info(f"✅ {len(images)} imagens encontradas")
                return {
                    'success': True,
                    'images': images,
                    'source': domain,
                    'credit': self._generate_image_credit(domain)
                }
            else:
                logger.info("⚠ Nenhuma imagem encontrada")
                return {'success': False, 'images': [], 'source': domain}
                
        except Exception as e:
            logger.error(f"❌ Erro ao extrair imagens: {e}")
            return {'success': False, 'images': [], 'error': str(e)}
    
    def _extract_images_with_selectors(self, soup, domain, base_url):
        """Extrai imagens usando seletores específicos do site"""
        images = []
        
        # Obter seletores para o site
        selectors = self.image_selectors.get(domain, {})
        
        # Tentar seletores principais primeiro
        for selector_type in ['main_image', 'gallery_images', 'fallback']:
            if selector_type in selectors:
                for selector in selectors[selector_type]:
                    elements = soup.select(selector)
                    for element in elements:
                        img_data = self._process_image_element(element, base_url)
                        if img_data and img_data not in images:
                            images.append(img_data)
                
                # Se encontrou imagens, parar aqui
                if images:
                    break
        
        return images[:3]  # Limitar a 3 imagens
    
    def _process_image_element(self, element, base_url):
        """Processa elemento de imagem"""
        try:
            # Obter URL da imagem
            img_src = element.get('src') or element.get('data-src')
            if not img_src:
                return None
            
            # Converter URL relativa para absoluta
            img_url = urljoin(base_url, img_src)
            
            # Obter alt text
            alt_text = element.get('alt', '')
            
            # Obter caption se disponível
            caption = ""
            parent = element.parent
            if parent:
                caption_elem = parent.find(['figcaption', '.caption', '.image-caption'])
                if caption_elem:
                    caption = caption_elem.get_text().strip()
            
            return {
                'url': img_url,
                'alt': alt_text,
                'caption': caption,
                'width': element.get('width', ''),
                'height': element.get('height', '')
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar imagem: {e}")
            return None
    
    def _generate_image_credit(self, domain):
        """Gera crédito da imagem baseado no site (uso editorial)"""
        credit_mapping = {
            'oglobo.globo.com': 'Foto: O Globo (Uso Editorial)',
            'g1.globo.com': 'Foto: G1 (Uso Editorial)',
            'folha.uol.com.br': 'Foto: Folha de S.Paulo (Uso Editorial)',
            'estadao.com.br': 'Foto: Estadão (Uso Editorial)',
            'cnnbrasil.com.br': 'Foto: CNN Brasil (Uso Editorial)',
            'infomoney.com.br': 'Foto: InfoMoney (Uso Editorial)'
        }
        
        return credit_mapping.get(domain, f"Foto: {domain} (Uso Editorial)")
    
    def get_best_image(self, images_data):
        """Seleciona a melhor imagem da lista"""
        if not images_data or not images_data.get('images'):
            return None
        
        images = images_data['images']
        
        # Priorizar imagem principal (primeira)
        if images:
            best_image = images[0]
            best_image['credit'] = images_data.get('credit', 'Foto: Fonte Original')
            return best_image
        
        return None
