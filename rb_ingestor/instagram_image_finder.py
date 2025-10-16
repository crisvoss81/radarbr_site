import requests
import re
import logging
from typing import Dict, List, Optional
from urllib.parse import urlparse
import json

logger = logging.getLogger(__name__)

class InstagramImageFinder:
    def __init__(self):
        self.public_figures = {
            # Políticos brasileiros
            'lula': ['@lula', '@lulaoficial', '@luiz_inacio_lula_da_silva'],
            'bolsonaro': ['@jairbolsonaro', '@bolsonaro'],
            'marina silva': ['@marinasilva', '@marina_silva'],
            'ciro gomes': ['@cirogomes', '@ciro_gomes'],
            'doria': ['@joaodoria', '@joao_doria'],
            
            # Celebridades internacionais
            'katy perry': ['@katyperry'],
            'justin trudeau': ['@justinpjtrudeau'],
            'elon musk': ['@elonmusk'],
            'taylor swift': ['@taylorswift'],
            'cristiano ronaldo': ['@cristiano'],
            'messi': ['@leomessi'],
            
            # Celebridades brasileiras
            'anitta': ['@anitta'],
            'luciano huck': ['@lucianohuck'],
            'faustão': ['@faustao'],
            'silvio santos': ['@silviosantos'],
            'gloria maria': ['@gloriamaria'],
            
            # Atletas brasileiros
            'neymar': ['@neymarjr'],
            'ronaldinho': ['@ronaldinho'],
            'romario': ['@romario'],
            'pelé': ['@pele'],
            
            # Jornalistas e apresentadores
            'william bonner': ['@williambonner'],
            'fatima bernardes': ['@fatimabernardes'],
            'patricia poeta': ['@patriciapoeta'],
            'ana maria braga': ['@anamariabraga'],
            
            # Empresários
            'abilio diniz': ['@abiliodiniz'],
            'luiza helena trajano': ['@luizahelenatrajano'],
            'jorge paulo lemann': ['@jorgepaulolemann']
        }
        
        self.instagram_patterns = [
            r'instagram\.com/([^/\s]+)',
            r'@([a-zA-Z0-9_.]+)',
            r'instagram\.com/p/([^/\s]+)',
            r'instagram\.com/reel/([^/\s]+)',
            r'instagram\.com/tv/([^/\s]+)'
        ]

    def extract_instagram_mentions(self, text: str) -> List[str]:
        """Extrai menções do Instagram do texto"""
        mentions = []
        text_lower = text.lower()
        
        # Buscar padrões de Instagram
        for pattern in self.instagram_patterns:
            matches = re.findall(pattern, text_lower)
            mentions.extend(matches)
        
        # Buscar figuras públicas mencionadas
        for figure, handles in self.public_figures.items():
            if figure in text_lower:
                mentions.extend(handles)
        
        return list(set(mentions))  # Remove duplicatas

    def find_public_figure_instagram(self, text: str) -> Optional[Dict]:
        """Encontra Instagram de figura pública mencionada no texto"""
        text_lower = text.lower()
        
        for figure, handles in self.public_figures.items():
            if figure in text_lower:
                # Retornar o primeiro handle encontrado
                return {
                    'figure': figure.title(),
                    'instagram_handle': handles[0],
                    'instagram_url': f"https://www.instagram.com/{handles[0].replace('@', '')}/",
                    'confidence': 'high'
                }
        
        return None

    def get_instagram_profile_image(self, username: str) -> Optional[Dict]:
        """Obtém imagem do perfil do Instagram (simulado - Instagram não permite acesso direto)"""
        try:
            # NOTA: Instagram não permite acesso direto às imagens via API pública
            # Este é um placeholder para futuras implementações
            
            # Para figuras públicas conhecidas, podemos usar URLs conhecidas
            known_profile_images = {
                'lula': 'https://example.com/lula-profile.jpg',
                'katyperry': 'https://example.com/katy-profile.jpg',
                'neymarjr': 'https://example.com/neymar-profile.jpg'
            }
            
            if username.lower() in known_profile_images:
                return {
                    'url': known_profile_images[username.lower()],
                    'alt': f"Foto do perfil do Instagram de {username}",
                    'credit': f"Foto: Instagram @{username}",
                    'source': 'instagram_profile'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar imagem do Instagram: {e}")
            return None

    def search_instagram_content(self, query: str) -> Optional[Dict]:
        """Busca conteúdo do Instagram relacionado (simulado)"""
        try:
            # NOTA: Instagram não permite busca pública de conteúdo
            # Este é um placeholder para futuras implementações
            
            # Simular busca por hashtags relacionadas
            hashtags = self._extract_hashtags(query)
            
            if hashtags:
                return {
                    'hashtags': hashtags,
                    'suggested_content': f"Buscar por #{hashtags[0]} no Instagram",
                    'instagram_url': f"https://www.instagram.com/explore/tags/{hashtags[0]}/"
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar conteúdo do Instagram: {e}")
            return None

    def _extract_hashtags(self, text: str) -> List[str]:
        """Extrai hashtags do texto"""
        hashtag_pattern = r'#([a-zA-Z0-9_]+)'
        hashtags = re.findall(hashtag_pattern, text.lower())
        
        # Adicionar hashtags baseadas no conteúdo
        content_hashtags = []
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['política', 'eleição', 'presidente']):
            content_hashtags.extend(['politica', 'eleicao', 'brasil'])
        
        if any(word in text_lower for word in ['celebridade', 'famoso', 'artista']):
            content_hashtags.extend(['celebridade', 'famoso', 'artista'])
        
        if any(word in text_lower for word in ['esporte', 'futebol', 'atleta']):
            content_hashtags.extend(['esporte', 'futebol', 'atleta'])
        
        return list(set(hashtags + content_hashtags))

    def extract_social_media_images_from_news(self, news_article: Dict) -> Optional[Dict]:
        """Extrai imagens de redes sociais do artigo original"""
        if not news_article or not news_article.get('url'):
            return None
        
        try:
            import requests
            from bs4 import BeautifulSoup
            
            url = news_article['url']
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar imagens que parecem ser de redes sociais
            social_images = []
            
            # Padrões para identificar imagens de redes sociais
            social_patterns = [
                'instagram', 'twitter', 'facebook', 'social', 'profile', 'avatar'
            ]
            
            for img in soup.find_all('img', src=True):
                img_src = img['src'].lower()
                img_alt = img.get('alt', '').lower()
                
                # Verificar se a imagem parece ser de rede social
                if any(pattern in img_src or pattern in img_alt for pattern in social_patterns):
                    social_images.append({
                        'url': img['src'],
                        'alt': img.get('alt', ''),
                        'credit': f"Foto: {urlparse(url).netloc}",
                        'source': 'news_social_media'
                    })
            
            if social_images:
                return social_images[0]  # Retornar a primeira encontrada
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao extrair imagens de redes sociais: {e}")
            return None

    def get_instagram_image_for_article(self, article_title: str, article_content: str, news_article: Dict = None) -> Optional[Dict]:
        """Obtém imagem do Instagram para o artigo seguindo a lógica específica"""
        try:
            # Combinar texto do artigo e notícia original
            full_text = f"{article_title} {article_content}"
            if news_article:
                full_text += f" {news_article.get('title', '')} {news_article.get('description', '')}"
            
            # 1. PRIORIDADE: Verificar se é sobre figura pública
            public_figure = self.find_public_figure_instagram(full_text)
            if not public_figure:
                # Se não é figura pública, não usar Instagram
                return None
            
            logger.info(f"🎭 Figura pública detectada: {public_figure['figure']}")
            
            # 2. PRIORIDADE 1: Buscar imagem de rede social no artigo original
            if news_article:
                social_image = self.extract_social_media_images_from_news(news_article)
                if social_image:
                    logger.info("📱 Imagem de rede social encontrada no artigo original")
                    return {
                        **social_image,
                        'figure_name': public_figure['figure'],
                        'instagram_handle': public_figure['instagram_handle'],
                        'instagram_url': public_figure['instagram_url'],
                        'source': 'news_social_media'
                    }
            
            # 3. PRIORIDADE 2: Buscar imagem do Instagram oficial da figura
            profile_image = self.get_instagram_profile_image(public_figure['instagram_handle'].replace('@', ''))
            if profile_image:
                logger.info(f"📱 Imagem do Instagram oficial encontrada: {public_figure['instagram_handle']}")
                return {
                    **profile_image,
                    'figure_name': public_figure['figure'],
                    'instagram_handle': public_figure['instagram_handle'],
                    'instagram_url': public_figure['instagram_url'],
                    'source': 'instagram_official'
                }
            
            # 4. Se não encontrou imagem do Instagram, retornar None (usar banco gratuito)
            logger.info("📱 Nenhuma imagem do Instagram encontrada - usar banco gratuito")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar imagem do Instagram: {e}")
            return None
