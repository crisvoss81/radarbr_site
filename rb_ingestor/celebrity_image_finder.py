# rb_ingestor/celebrity_image_finder.py
"""
Sistema para encontrar imagens de figuras públicas nas redes sociais
"""
import re
import requests
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class CelebrityImageFinder:
    """Sistema para encontrar imagens de figuras públicas"""
    
    def __init__(self):
        # Base de dados de figuras públicas e suas redes sociais
        self.celebrity_profiles = {
            # Cantores/Músicos
            'katy perry': {
                'instagram': '@katyperry',
                'twitter': '@katyperry',
                'category': 'música'
            },
            'justin trudeau': {
                'instagram': '@justinpjtrudeau',
                'twitter': '@justinpjtrudeau',
                'category': 'política'
            },
            'lula': {
                'instagram': '@lulaoficial',
                'twitter': '@lulaoficial',
                'category': 'política'
            },
            'bolsonaro': {
                'instagram': '@jairbolsonaro',
                'twitter': '@jairbolsonaro',
                'category': 'política'
            },
            'anitta': {
                'instagram': '@anitta',
                'twitter': '@anitta',
                'category': 'música'
            },
            'luisa sonza': {
                'instagram': '@luisasonza',
                'twitter': '@luisasonza',
                'category': 'música'
            },
            'whindersson nunes': {
                'instagram': '@whindersson',
                'twitter': '@whindersson',
                'category': 'humor'
            },
            
            # Atletas
            'neymar': {
                'instagram': '@neymarjr',
                'twitter': '@neymarjr',
                'category': 'esportes'
            },
            'ronaldinho': {
                'instagram': '@ronaldinho',
                'twitter': '@10ronaldinho',
                'category': 'esportes'
            },
            
            # Atores/Atrizes
            'paolla oliveira': {
                'instagram': '@paollaoliveira',
                'twitter': '@paollaoliveira',
                'category': 'televisão'
            },
            'bruna marquezine': {
                'instagram': '@brunamarquezine',
                'twitter': '@brunamarquezine',
                'category': 'televisão'
            }
        }
    
    def find_celebrities_in_content(self, content: str) -> List[Dict]:
        """Encontra figuras públicas mencionadas no conteúdo"""
        content_lower = content.lower()
        found_celebrities = []
        
        for celebrity, profile in self.celebrity_profiles.items():
            if celebrity in content_lower:
                found_celebrities.append({
                    'name': celebrity.title(),
                    'instagram': profile['instagram'],
                    'twitter': profile['twitter'],
                    'category': profile['category']
                })
        
        return found_celebrities
    
    def generate_celebrity_image_prompt(self, celebrities: List[Dict]) -> str:
        """Gera prompt para busca de imagem de figuras públicas"""
        if not celebrities:
            return ""
        
        celebrity_names = [celeb['name'] for celeb in celebrities]
        instagram_handles = [celeb['instagram'] for celeb in celebrities]
        
        prompt = f"""
        Buscar imagem de: {', '.join(celebrity_names)}
        Instagram: {', '.join(instagram_handles)}
        
        IMPORTANTE: Dar créditos adequados:
        - "Foto: Instagram/{instagram_handles[0]}" se encontrar
        - Usar imagem oficial das redes sociais
        - Priorizar fotos recentes e de qualidade
        """
        
        return prompt
    
    def get_image_credit(self, celebrity: Dict) -> str:
        """Gera crédito da imagem"""
        return f"Foto: Instagram/{celebrity['instagram']}"
    
    def should_use_celebrity_image(self, celebrities: List[Dict], topic: str) -> bool:
        """Determina se deve usar imagem de figura pública"""
        if not celebrities:
            return False
        
        # Se o tópico menciona figuras públicas, priorizar suas imagens
        topic_lower = topic.lower()
        for celebrity in celebrities:
            if celebrity['name'].lower() in topic_lower:
                return True
        
        return False



