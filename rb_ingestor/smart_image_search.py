# rb_ingestor/smart_image_search.py
"""
Sistema inteligente de busca de imagem usando Google Lens
"""
from typing import Dict, Optional, List
from rb_ingestor.google_lens_analyzer import google_lens_analyzer
from rb_ingestor.image_analyzer import image_analyzer

class SmartImageSearch:
    """Sistema inteligente de busca de imagem usando Google Lens"""
    
    def __init__(self):
        self.google_lens = google_lens_analyzer
        self.image_extractor = image_analyzer
    
    def find_smart_image_for_article(self, news_url: str, article_title: str = "") -> Optional[Dict]:
        """Busca imagem inteligente para artigo usando Google Lens"""
        try:
            print(f"🔍 Buscando imagem inteligente para: {article_title[:50]}...")
            
            # 1. Extrair imagem da notícia original
            original_image_url = self.image_extractor.extract_main_image_from_url(news_url)
            
            if not original_image_url:
                print("❌ Nenhuma imagem encontrada na notícia original")
                return None
            
            print(f"📸 Imagem original encontrada: {original_image_url}")
            
            # 2. Google Lens analisa e busca imagens similares
            lens_result = self.google_lens.find_similar_images(original_image_url, max_results=6)
            
            if not lens_result['success']:
                print(f"❌ Google Lens falhou: {lens_result.get('error', 'Erro desconhecido')}")
                return None
            
            # 3. Selecionar melhor imagem baseada na similaridade
            similar_images = lens_result['similar_images']
            
            if not similar_images:
                print("❌ Nenhuma imagem similar encontrada")
                return None
            
            # Pegar a imagem com maior similaridade
            best_image = similar_images[0]
            
            print(f"✅ Imagem similar encontrada: {best_image['source'].upper()} (similaridade: {best_image['similarity_score']:.2f})")
            
            return {
                'url': best_image['url'],
                'alt': best_image['alt'] or f"Imagem relacionada a {article_title[:50]}",
                'credit': best_image['credit'],
                'source': best_image['source'],
                'similarity_score': best_image['similarity_score'],
                'original_image': original_image_url,
                'google_lens_analysis': lens_result['google_lens_analysis'],
                'search_method': 'google_lens_visual_search'
            }
            
        except Exception as e:
            print(f"❌ Erro na busca inteligente de imagem: {e}")
            return None
    
    def get_fallback_image(self, article_title: str) -> Dict:
        """Fallback para imagem quando Google Lens falha"""
        return {
            'url': "/static/img/default-news.webp",
            'alt': article_title,
            'credit': "RadarBR",
            'source': 'fallback',
            'similarity_score': 0.0,
            'search_method': 'fallback_static'
        }

# Instância global
smart_image_search = SmartImageSearch()
