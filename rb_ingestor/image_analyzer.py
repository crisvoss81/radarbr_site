# rb_ingestor/image_analyzer.py
"""
Sistema de análise de imagem para busca de imagens similares
"""
import os
import requests
import base64
from typing import Dict, Optional, List
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

class ImageAnalyzer:
    """Analisa imagens de notícias para buscar imagens similares"""
    
    def __init__(self):
        self.openai_client = None
        if OpenAI and os.getenv("OPENAI_API_KEY"):
            self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def extract_main_image_from_url(self, url: str) -> Optional[str]:
        """Extrai a imagem principal de uma URL de notícia"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar imagem principal (várias estratégias)
            image_url = None
            
            # 1. Meta tag og:image
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                image_url = og_image['content']
            
            # 2. Meta tag twitter:image
            if not image_url:
                twitter_image = soup.find('meta', name='twitter:image')
                if twitter_image and twitter_image.get('content'):
                    image_url = twitter_image['content']
            
            # 3. Primeira imagem grande no artigo
            if not image_url:
                images = soup.find_all('img')
                for img in images:
                    src = img.get('src') or img.get('data-src')
                    if src:
                        # Filtrar imagens pequenas (provavelmente ícones)
                        width = img.get('width', '')
                        height = img.get('height', '')
                        if (isinstance(width, str) and width.isdigit() and int(width) > 200) or \
                           (isinstance(height, str) and height.isdigit() and int(height) > 200):
                            image_url = src
                            break
            
            # Converter URL relativa para absoluta
            if image_url and not image_url.startswith('http'):
                image_url = urljoin(url, image_url)
            
            return image_url
            
        except Exception as e:
            print(f"Erro ao extrair imagem de {url}: {e}")
            return None
    
    def analyze_image_with_ai(self, image_url: str) -> Optional[Dict]:
        """Analisa uma imagem usando OpenAI Vision API"""
        if not self.openai_client:
            print("OpenAI client não disponível")
            return None
        
        try:
            # Baixar a imagem
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            
            # Codificar em base64
            image_base64 = base64.b64encode(response.content).decode('utf-8')
            
            # Analisar com OpenAI Vision
            analysis = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analise esta imagem e forneça:
1. Descrição detalhada do que está na imagem
2. Palavras-chave principais (máximo 10)
3. Cores predominantes
4. Tipo de imagem (foto, gráfico, ilustração, etc.)
5. Contexto provável (política, tecnologia, esportes, etc.)

Responda em português brasileiro e seja específico."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            result = analysis.choices[0].message.content
            
            return {
                'description': result,
                'image_url': image_url,
                'analysis_success': True
            }
            
        except Exception as e:
            print(f"Erro ao analisar imagem {image_url}: {e}")
            return {
                'description': None,
                'image_url': image_url,
                'analysis_success': False,
                'error': str(e)
            }
    
    def generate_search_keywords_from_analysis(self, analysis: str) -> List[str]:
        """Gera palavras-chave de busca baseadas na análise da imagem"""
        if not analysis:
            return []
        
        # Extrair palavras-chave da análise
        keywords = []
        
        # Palavras-chave comuns para busca de imagem
        common_keywords = [
            'pessoa', 'homem', 'mulher', 'grupo', 'pessoas',
            'edifício', 'prédio', 'cidade', 'urbano',
            'natureza', 'paisagem', 'céu', 'montanha',
            'tecnologia', 'computador', 'smartphone', 'tela',
            'política', 'governo', 'presidente', 'ministro',
            'economia', 'dinheiro', 'gráfico', 'crescimento',
            'esporte', 'futebol', 'atleta', 'competição',
            'saúde', 'médico', 'hospital', 'vacina'
        ]
        
        analysis_lower = analysis.lower()
        
        for keyword in common_keywords:
            if keyword in analysis_lower:
                keywords.append(keyword)
        
        # Adicionar palavras específicas da análise
        words = analysis.split()
        for word in words:
            if len(word) > 4 and word.isalpha():
                keywords.append(word.lower())
        
        # Limitar a 8 palavras-chave mais relevantes
        return keywords[:8]
    
    def analyze_news_image(self, news_url: str) -> Optional[Dict]:
        """Processo completo: extrai e analisa imagem de uma notícia"""
        print(f"🔍 Analisando imagem da notícia: {news_url}")
        
        # 1. Extrair imagem principal
        image_url = self.extract_main_image_from_url(news_url)
        if not image_url:
            print("❌ Nenhuma imagem encontrada na notícia")
            return None
        
        print(f"✅ Imagem encontrada: {image_url}")
        
        # 2. Analisar com IA
        analysis_result = self.analyze_image_with_ai(image_url)
        if not analysis_result or not analysis_result.get('analysis_success'):
            print("❌ Falha na análise da imagem")
            return None
        
        print("✅ Imagem analisada com sucesso")
        
        # 3. Gerar palavras-chave
        keywords = self.generate_search_keywords_from_analysis(analysis_result['description'])
        
        return {
            'original_image_url': image_url,
            'analysis': analysis_result['description'],
            'search_keywords': keywords,
            'success': True
        }

# Instância global
image_analyzer = ImageAnalyzer()
