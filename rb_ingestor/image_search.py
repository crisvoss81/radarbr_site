# rb_ingestor/image_search.py
"""
Sistema inteligente de busca e criação de imagens para notícias.
Integra com APIs gratuitas e gera URLs de imagens relevantes.
"""

import os
import re
import requests
import time
from typing import Optional, List, Dict, Tuple
from urllib.parse import quote
import logging

logger = logging.getLogger(__name__)

class ImageSearchEngine:
    """Motor de busca de imagens que integra múltiplas APIs gratuitas."""
    
    def __init__(self):
        self.unsplash_key = os.getenv('UNSPLASH_API_KEY')
        self.pexels_key = os.getenv('PEXELS_API_KEY')
        self.pixabay_key = os.getenv('PIXABAY_API_KEY')
        
        # Cache simples em memória
        self._cache = {}
        
        # Headers para requests
        self.headers = {
            'User-Agent': 'RadarBR/1.0 (News Aggregator)'
        }
    
    def extract_keywords(self, title: str, content: str = "") -> List[str]:
        """
        Extrai palavras-chave RELEVANTES do título focando em termos específicos.
        Prioriza termos concretos que terão imagens específicas disponíveis.
        """
        # FOCAR APENAS NO TÍTULO (mais específico)
        text = title.lower()
        
        # Remover caracteres especiais e dividir em palavras
        words = re.findall(r'\b\w+\b', text)
        
        # STOP WORDS expandido
        stop_words = {
            # Artigos, preposições, conjunções
            'a', 'o', 'as', 'os', 'um', 'uma', 'de', 'da', 'do', 'das', 'dos',
            'em', 'na', 'no', 'nas', 'nos', 'para', 'por', 'com', 'sem', 'sob',
            'sobre', 'atrás', 'através', 'entre', 'durante', 'até', 'desde',
            # Conjunções
            'que', 'se', 'mas', 'porém', 'porque', 'como', 'quando', 'onde',
            'então', 'logo', 'assim', 'portanto', 'ou', 'e', 'nem', 'também',
            # Pronomes
            'ele', 'ela', 'eles', 'elas', 'eu', 'nós', 'vós', 'você', 'vocês',
            'seu', 'sua', 'seus', 'suas', 'meu', 'minha', 'meus', 'minhas',
            # Verbos comuns
            'ser', 'ter', 'estar', 'haver', 'fazer', 'dizer', 'ir', 'vir',
            'ver', 'dar', 'chegar', 'ficar', 'passar', 'sair', 'entrar',
            'abrir', 'fechar', 'começar', 'terminar', 'acabar', 'iniciar',
            # Palavras genéricas
            'muito', 'mais', 'menos', 'bem', 'mal', 'melhor', 'pior',
            'grande', 'pequeno', 'novo', 'velho', 'junto', 'sozinho',
            'hoje', 'ontem', 'amanhã', 'agora', 'depois', 'antes',
            # Números
            'um', 'dois', 'três', 'quatro', 'cinco', 'dez', 'mil'
        }
        
        # EXTRAIR APENAS TERMOS CONCRETOS E ESPECÍFICOS
        keywords = []
        for word in words:
            if (len(word) >= 4 and 
                word not in stop_words and 
                word.isalpha() and
                word not in keywords):
                keywords.append(word)
        
        # Remover termos muito genéricos mesmo depois do filtro
        generic_terms = {
            'notícia', 'noticia', 'artigo', 'matéria', 'materia', 'reportagem',
            'reportagem', 'texto', 'conteúdo', 'conteudo', 'informação',
            'informacao', 'dados', 'resultado', 'resultados', 'estudo',
            'pesquisa', 'análise', 'analise', 'relatório', 'relatorio'
        }
        
        keywords = [w for w in keywords if w not in generic_terms]
        
        # LIMITAR A 3-4 TERMOS MAIS RELEVANTES (mais específico)
        return keywords[:4]
    
    def search_unsplash(self, keywords: List[str]) -> Optional[str]:
        """Busca imagem no Unsplash."""
        if not self.unsplash_key:
            return None
        
        try:
            query = " ".join(keywords[:3])  # Máximo 3 palavras para Unsplash
            url = f"https://api.unsplash.com/search/photos"
            
            params = {
                'query': query,
                'per_page': 1,
                'orientation': 'landscape',
                'content_filter': 'high'
            }
            
            headers = {
                **self.headers,
                'Authorization': f'Client-ID {self.unsplash_key}'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('results'):
                photo = data['results'][0]
                return photo['urls']['regular']  # URL da imagem
            
        except Exception as e:
            logger.warning(f"Erro ao buscar no Unsplash: {e}")
        
        return None
    
    def search_pexels(self, keywords: List[str]) -> Optional[str]:
        """Busca imagem no Pexels."""
        if not self.pexels_key:
            return None
        
        try:
            query = " ".join(keywords[:3])
            url = f"https://api.pexels.com/v1/search"
            
            params = {
                'query': query,
                'per_page': 1,
                'orientation': 'landscape'
            }
            
            headers = {
                **self.headers,
                'Authorization': self.pexels_key
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('photos'):
                photo = data['photos'][0]
                return photo['src']['large']  # URL da imagem
            
        except Exception as e:
            logger.warning(f"Erro ao buscar no Pexels: {e}")
        
        return None
    
    def search_pixabay(self, keywords: List[str]) -> Optional[str]:
        """Busca imagem no Pixabay."""
        if not self.pixabay_key:
            return None
        
        try:
            query = " ".join(keywords[:3])
            url = f"https://pixabay.com/api/"
            
            params = {
                'key': self.pixabay_key,
                'q': query,
                'per_page': 3,
                'image_type': 'photo',
                'orientation': 'horizontal',
                'category': 'backgrounds',
                'min_width': 800,
                'min_height': 600
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('hits'):
                photo = data['hits'][0]
                return photo['webformatURL']  # URL da imagem
            
        except Exception as e:
            logger.warning(f"Erro ao buscar no Pixabay: {e}")
        
        return None
    
    def validate_image_url(self, url: str) -> bool:
        """Valida se a URL da imagem é acessível."""
        try:
            response = requests.head(url, headers=self.headers, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def search_image(self, title: str, content: str = "", category: str = "") -> Optional[str]:
        """
        Busca uma imagem relevante para a notícia.
        Tenta múltiplas APIs em ordem de preferência.
        """
        # Verificar cache primeiro
        cache_key = f"{title[:50]}_{category}"
        if cache_key in self._cache:
            cached_url = self._cache[cache_key]
            if self.validate_image_url(cached_url):
                return cached_url
            else:
                # Remover do cache se não for mais válida
                del self._cache[cache_key]
        
        # Extrair palavras-chave
        keywords = self.extract_keywords(title, content)
        
        # Adicionar categoria se disponível
        if category and category.lower() not in ['geral', 'general']:
            keywords.insert(0, category.lower())
        
        if not keywords:
            return None
        
        logger.info(f"Buscando imagem para: {title[:50]}... Keywords: {keywords}")
        
        # Tentar APIs em ordem de preferência
        apis = [
            ('unsplash', self.search_unsplash),
            ('pexels', self.search_pexels),
            ('pixabay', self.search_pixabay)
        ]
        
        for api_name, search_func in apis:
            try:
                image_url = search_func(keywords)
                if image_url and self.validate_image_url(image_url):
                    # Cachear resultado
                    self._cache[cache_key] = image_url
                    logger.info(f"Imagem encontrada via {api_name}: {image_url}")
                    return image_url
                
                # Pequena pausa entre APIs
                time.sleep(0.5)
                
            except Exception as e:
                logger.warning(f"Erro na API {api_name}: {e}")
                continue
        
        logger.warning(f"Nenhuma imagem encontrada para: {title[:50]}")
        return None
    
    def get_category_image(self, category: str) -> Optional[str]:
        """Busca imagem genérica para uma categoria."""
        category_keywords = {
            'agro': ['agriculture', 'farm', 'crops'],
            'brasil': ['brazil', 'brasil', 'flag'],
            'carros-mobilidade': ['car', 'automobile', 'transport'],
            'cidades-rs': ['city', 'urban', 'rio grande do sul'],
            'ciencia-meio-ambiente': ['science', 'environment', 'nature'],
            'economia': ['economy', 'money', 'business'],
            'educacao': ['education', 'school', 'learning'],
            'entretenimento': ['entertainment', 'music', 'movie'],
            'esportes': ['sports', 'football', 'athlete'],
            'geral': ['news', 'general', 'information'],
            'justica-seguranca': ['justice', 'law', 'security'],
            'loterias': ['lottery', 'luck', 'gambling'],
            'mundo': ['world', 'global', 'international'],
            'politica': ['politics', 'government', 'election'],
            'saude': ['health', 'medical', 'hospital'],
            'tecnologia': ['technology', 'computer', 'digital'],
            'trabalho-carreira': ['work', 'career', 'job'],
            'turismo': ['tourism', 'travel', 'vacation']
        }
        
        keywords = category_keywords.get(category.lower(), ['news', 'general'])
        return self.search_image(" ".join(keywords), category=category)


def find_image_for_news(title: str, content: str = "", category: str = "") -> Optional[str]:
    """
    Função principal para buscar imagem para uma notícia.
    Usado pelo sistema de ingestão.
    """
    engine = ImageSearchEngine()
    return engine.search_image(title, content, category)


def get_category_placeholder_image(category: str) -> Optional[str]:
    """
    Busca imagem genérica para uma categoria.
    Usado quando não há imagem específica.
    """
    engine = ImageSearchEngine()
    return engine.get_category_image(category)
