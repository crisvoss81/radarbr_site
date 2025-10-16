# rb_ingestor/ai_image_generator.py
"""
Sistema para geração de imagens usando IA baseado no título da notícia
"""
import os
import logging
import requests
import json
from typing import Optional, Dict, List
import re

logger = logging.getLogger(__name__)

class AIImageGenerator:
    """Sistema para gerar imagens usando IA baseado no título da notícia"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.dalle_model = "dall-e-3"
        
        # Palavras-chave que indicam tipos de imagem
        self.image_type_keywords = {
            'business': ['economia', 'mercado', 'finanças', 'investimento', 'bolsa', 'ações', 'dólar', 'inflação'],
            'politics': ['política', 'governo', 'eleições', 'presidente', 'ministro', 'congresso', 'senado'],
            'sports': ['esportes', 'futebol', 'copa', 'mundial', 'jogador', 'time', 'clube', 'estádio'],
            'technology': ['tecnologia', 'ciência', 'inovação', 'digital', 'internet', 'smartphone', 'computador'],
            'health': ['saúde', 'medicina', 'hospital', 'vacina', 'covid', 'tratamento', 'médico'],
            'environment': ['meio ambiente', 'natureza', 'clima', 'sustentabilidade', 'energia', 'verde'],
            'entertainment': ['celebridade', 'famoso', 'artista', 'música', 'cinema', 'televisão', 'show'],
            'education': ['educação', 'escola', 'universidade', 'professor', 'estudante', 'ensino'],
            'culture': ['cultura', 'arte', 'museu', 'teatro', 'literatura', 'história', 'tradição']
        }
    
    def generate_image_from_news_title(self, news_title: str, news_description: str = "") -> Optional[Dict]:
        """
        Gera imagem usando IA baseada no título da notícia
        """
        try:
            if not self.openai_api_key:
                logger.warning("OpenAI API key não configurada")
                return None
            
            # Criar prompt otimizado baseado no título
            prompt = self._create_image_prompt(news_title, news_description)
            
            logger.info(f"🎨 Gerando imagem com IA para: {news_title[:50]}...")
            
            # Gerar imagem usando DALL-E
            image_url = self._generate_with_dalle(prompt)
            
            if image_url:
                return {
                    'url': image_url,
                    'alt': f"Imagem gerada por IA para: {news_title}",
                    'credit': "Imagem gerada por IA (DALL-E)",
                    'license': "AI Generated",
                    'source': 'dalle_ai',
                    'prompt': prompt
                }
            
        except Exception as e:
            logger.error(f"Erro ao gerar imagem com IA: {e}")
        
        return None
    
    def _create_image_prompt(self, news_title: str, news_description: str = "") -> str:
        """
        Cria prompt otimizado para geração de imagem baseado no título
        """
        # Limpar e normalizar o título
        clean_title = self._clean_title_for_prompt(news_title)
        
        # Identificar tipo de imagem baseado no conteúdo
        image_type = self._identify_image_type(clean_title, news_description)
        
        # Criar prompt baseado no tipo identificado
        base_prompt = self._create_base_prompt(clean_title, image_type)
        
        # Adicionar elementos específicos baseados no título
        specific_elements = self._extract_specific_elements(clean_title)
        
        # Combinar elementos
        final_prompt = f"{base_prompt}, {specific_elements}"
        
        # Adicionar estilo e qualidade
        final_prompt += ", professional photography, high quality, realistic, Brazilian context"
        
        return final_prompt
    
    def _clean_title_for_prompt(self, title: str) -> str:
        """Limpa o título para uso no prompt"""
        # Remover caracteres especiais e normalizar
        clean = re.sub(r'[^\w\s]', ' ', title.lower())
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        # Remover palavras muito comuns que não agregam valor visual
        stop_words = {
            'notícia', 'noticia', 'últimas', 'ultimas', 'hoje', 'ontem', 'amanhã',
            'amanha', 'brasil', 'brasileiro', 'brasileira', 'nacional', 'mundial',
            'anuncia', 'anunciou', 'confirma', 'confirmou', 'divulga', 'divulgou',
            'aprova', 'aprovou', 'rejeita', 'rejeitou', 'cancela', 'cancelou'
        }
        
        words = clean.split()
        filtered_words = [w for w in words if w not in stop_words and len(w) > 2]
        
        return ' '.join(filtered_words[:8])  # Máximo 8 palavras
    
    def _identify_image_type(self, title: str, description: str = "") -> str:
        """Identifica o tipo de imagem baseado no conteúdo"""
        text = f"{title} {description}".lower()
        
        for image_type, keywords in self.image_type_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return image_type
        
        return 'general'
    
    def _create_base_prompt(self, clean_title: str, image_type: str) -> str:
        """Cria prompt base baseado no tipo de imagem"""
        base_prompts = {
            'business': "Professional business scene with charts, graphs, and financial elements",
            'politics': "Political scene with government buildings, flags, and official elements",
            'sports': "Dynamic sports scene with athletes, stadium, and sporting equipment",
            'technology': "Modern technology scene with computers, smartphones, and digital elements",
            'health': "Healthcare scene with medical equipment, doctors, and hospital elements",
            'environment': "Natural environment scene with trees, nature, and environmental elements",
            'entertainment': "Entertainment scene with celebrities, stage, and show elements",
            'education': "Educational scene with students, teachers, and school elements",
            'culture': "Cultural scene with art, museums, and cultural elements",
            'general': "Professional news scene with relevant elements"
        }
        
        return base_prompts.get(image_type, base_prompts['general'])
    
    def _extract_specific_elements(self, clean_title: str) -> str:
        """Extrai elementos específicos do título para o prompt"""
        elements = []
        
        # Detectar figuras públicas
        public_figures = {
            'lula': 'Brazilian politician in formal attire',
            'bolsonaro': 'Brazilian politician in formal attire',
            'neymar': 'Brazilian football player in sports attire',
            'anitta': 'Brazilian singer and celebrity',
            'marina silva': 'Brazilian politician in formal attire',
            'ciro gomes': 'Brazilian politician in formal attire',
            'doria': 'Brazilian politician in formal attire',
            'faustão': 'Brazilian TV presenter',
            'silvio santos': 'Brazilian businessman and TV host',
            'ronaldinho': 'Brazilian football player in sports attire',
            'romario': 'Brazilian football player in sports attire',
            'pelé': 'Brazilian football legend in sports attire'
        }
        
        for figure, description in public_figures.items():
            if figure in clean_title:
                elements.append(description)
                break
        
        # Detectar elementos específicos
        if 'dividendos' in clean_title:
            elements.append('financial charts and money symbols')
        elif 'inflação' in clean_title:
            elements.append('inflation charts and economic indicators')
        elif 'dólar' in clean_title:
            elements.append('dollar symbols and currency exchange')
        elif 'eleições' in clean_title:
            elements.append('voting booths and election materials')
        elif 'copa' in clean_title or 'mundial' in clean_title:
            elements.append('football stadium and World Cup elements')
        elif 'covid' in clean_title or 'vacina' in clean_title:
            elements.append('medical equipment and vaccination elements')
        elif 'energia' in clean_title:
            elements.append('energy sources and power plants')
        elif 'meio ambiente' in clean_title:
            elements.append('nature and environmental protection')
        
        return ', '.join(elements) if elements else 'relevant news elements'
    
    def _generate_with_dalle(self, prompt: str) -> Optional[str]:
        """Gera imagem usando DALL-E API"""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.openai_api_key)
            
            # Limitar tamanho do prompt
            if len(prompt) > 1000:
                prompt = prompt[:1000]
            
            response = client.images.generate(
                model=self.dalle_model,
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            logger.info(f"✅ Imagem gerada com sucesso: {image_url}")
            
            return image_url
            
        except Exception as e:
            logger.error(f"Erro na geração com DALL-E: {e}")
            return None
    
    def generate_fallback_image(self, news_title: str) -> Optional[Dict]:
        """
        Gera imagem de fallback quando outras opções falham
        """
        try:
            # Criar prompt mais simples e genérico
            clean_title = self._clean_title_for_prompt(news_title)
            
            # Prompt genérico mas relevante
            prompt = f"Professional news scene related to {clean_title}, Brazilian context, high quality, realistic"
            
            image_url = self._generate_with_dalle(prompt)
            
            if image_url:
                return {
                    'url': image_url,
                    'alt': f"Imagem gerada por IA para: {news_title}",
                    'credit': "Imagem gerada por IA (DALL-E)",
                    'license': "AI Generated",
                    'source': 'dalle_fallback',
                    'prompt': prompt
                }
            
        except Exception as e:
            logger.error(f"Erro ao gerar imagem de fallback: {e}")
        
        return None


