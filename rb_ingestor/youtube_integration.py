# rb_ingestor/youtube_integration.py
"""
Sistema para integração automática de vídeos do YouTube
"""
import re
import requests
from urllib.parse import urlparse, parse_qs
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class YouTubeIntegration:
    """Sistema para detectar e incorporar vídeos do YouTube automaticamente"""
    
    def __init__(self):
        # Padrões para detectar vídeos do YouTube
        self.youtube_patterns = [
            r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
            r'youtu\.be/([a-zA-Z0-9_-]{11})',
            r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
            r'youtube\.com/v/([a-zA-Z0-9_-]{11})',
            r'youtube\.com/user/[^/]+/.*#p/u/\d+/([a-zA-Z0-9_-]{11})',
        ]
        
        # Palavras-chave que indicam presença de vídeo
        self.video_keywords = [
            'vídeo', 'video', 'youtube', 'assista', 'veja', 'confira',
            'gravação', 'gravacao', 'filmagem', 'filmado', 'gravado',
            'transmissão', 'transmissao', 'ao vivo', 'live', 'streaming'
        ]
    
    def extract_video_id(self, text):
        """
        Extrai ID do vídeo do YouTube do texto
        """
        text_lower = text.lower()
        
        for pattern in self.youtube_patterns:
            match = re.search(pattern, text_lower)
            if match:
                video_id = match.group(1)
                logger.info(f"🎥 Vídeo do YouTube detectado: {video_id}")
                return video_id
        
        return None
    
    def has_video_mention(self, text):
        """
        Verifica se o texto menciona vídeos
        """
        text_lower = text.lower()
        
        for keyword in self.video_keywords:
            if keyword in text_lower:
                return True
        
        return False
    
    def search_related_video(self, topic, max_results=1):
        """
        Busca vídeos relacionados ao tema no YouTube
        """
        try:
            # Usar YouTube Data API v3 se disponível
            if hasattr(settings, 'YOUTUBE_API_KEY') and settings.YOUTUBE_API_KEY:
                return self._search_with_api(topic, max_results)
            else:
                # Fallback: buscar vídeos populares relacionados
                return self._search_popular_videos(topic)
                
        except Exception as e:
            logger.error(f"Erro ao buscar vídeos relacionados: {e}")
            return None
    
    def _search_with_api(self, topic, max_results):
        """
        Busca vídeos usando YouTube Data API
        """
        try:
            api_key = settings.YOUTUBE_API_KEY
            search_url = "https://www.googleapis.com/youtube/v3/search"
            
            params = {
                'part': 'snippet',
                'q': f"{topic} brasil",
                'type': 'video',
                'maxResults': max_results,
                'order': 'relevance',
                'key': api_key
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'items' in data and data['items']:
                video = data['items'][0]
                video_id = video['id']['videoId']
                title = video['snippet']['title']
                
                logger.info(f"🎥 Vídeo relacionado encontrado: {title}")
                return {
                    'id': video_id,
                    'title': title,
                    'source': 'youtube_api'
                }
            
        except Exception as e:
            logger.error(f"Erro na API do YouTube: {e}")
        
        return None
    
    def _search_popular_videos(self, topic):
        """
        Fallback: retorna vídeos populares relacionados ao tema
        """
        # Vídeos populares brasileiros por categoria
        popular_videos = {
            'economia': 'dQw4w9WgXcQ',  # Exemplo - substituir por vídeos reais
            'política': 'dQw4w9WgXcQ',
            'tecnologia': 'dQw4w9WgXcQ',
            'esportes': 'dQw4w9WgXcQ',
            'saúde': 'dQw4w9WgXcQ',
            'lazer': 'dQw4w9WgXcQ',
            'meio ambiente': 'dQw4w9WgXcQ',
            'mundo': 'dQw4w9WgXcQ',
            'brasil': 'dQw4w9WgXcQ'
        }
        
        topic_lower = topic.lower()
        
        for category, video_id in popular_videos.items():
            if category in topic_lower:
                logger.info(f"🎥 Vídeo popular encontrado para {category}")
                return {
                    'id': video_id,
                    'title': f"Vídeo relacionado a {category}",
                    'source': 'popular_fallback'
                }
        
        return None
    
    def generate_embed_code(self, video_id, title="Vídeo Relacionado"):
        """
        Gera código HTML para embed do YouTube
        """
        embed_code = f'''
        <div class="youtube-video-container" style="margin: 20px 0; text-align: center;">
            <div class="video-wrapper" style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; background: #000;">
                <iframe 
                    src="https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1&showinfo=0" 
                    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;"
                    allowfullscreen
                    title="{title}">
                </iframe>
            </div>
            <p class="video-caption" style="margin-top: 10px; font-size: 14px; color: #666; font-style: italic;">
                📺 {title}
            </p>
        </div>
        '''
        
        return embed_code
    
    def integrate_video_into_content(self, content, topic, article_title="", news_article=None):
        """
        Integra vídeo do YouTube no conteúdo do artigo baseado na notícia original
        """
        # 1. Verificar se já existe vídeo no conteúdo
        if 'youtube.com/embed' in content or 'youtu.be' in content:
            logger.info("🎥 Vídeo já presente no conteúdo")
            return content
        
        # 2. PRIORIDADE MÁXIMA: Extrair vídeo da notícia original
        if news_article:
            # Tentar extrair vídeo da URL da notícia original
            news_url = news_article.get('url', '')
            if news_url:
                video_id = self.extract_video_id(news_url)
                if video_id:
                    logger.info(f"🎥 Vídeo da notícia original: {video_id}")
                    embed_code = self.generate_embed_code(video_id, "Vídeo da Notícia Original")
                    
                    # Inserir vídeo após o primeiro parágrafo
                    paragraphs = content.split('</p>')
                    if len(paragraphs) > 1:
                        paragraphs.insert(1, embed_code)
                        return '</p>'.join(paragraphs)
                    else:
                        return content + embed_code
            
            # Tentar extrair vídeo do título/descrição da notícia
            news_title = news_article.get('title', '')
            news_description = news_article.get('description', '')
            news_text = f"{news_title} {news_description}"
            
            video_id = self.extract_video_id(news_text)
            if video_id:
                logger.info(f"🎥 Vídeo encontrado na notícia original: {video_id}")
                embed_code = self.generate_embed_code(video_id, "Vídeo da Notícia Original")
                
                # Inserir vídeo após o primeiro parágrafo
                paragraphs = content.split('</p>')
                if len(paragraphs) > 1:
                    paragraphs.insert(1, embed_code)
                    return '</p>'.join(paragraphs)
                else:
                    return content + embed_code
        
        # 3. FALLBACK: Tentar extrair vídeo do conteúdo gerado
        video_id = self.extract_video_id(content)
        
        if video_id:
            logger.info(f"🎥 Vídeo extraído do conteúdo gerado: {video_id}")
            embed_code = self.generate_embed_code(video_id, "Vídeo Relacionado")
            
            # Inserir vídeo após o primeiro parágrafo
            paragraphs = content.split('</p>')
            if len(paragraphs) > 1:
                paragraphs.insert(1, embed_code)
                return '</p>'.join(paragraphs)
            else:
                return content + embed_code
        
    def integrate_video_into_content(self, content, topic, article_title="", news_article=None):
        """
        Integra vídeo do YouTube APENAS se a notícia original tiver vídeo
        """
        # 1. Verificar se já existe vídeo no conteúdo
        if 'youtube.com/embed' in content or 'youtu.be' in content:
            logger.info("🎥 Vídeo já presente no conteúdo")
            return content
        
        # 2. PRIORIDADE MÁXIMA: Extrair vídeo da notícia original
        if news_article:
            # Tentar extrair vídeo da URL da notícia original
            news_url = news_article.get('url', '')
            if news_url:
                video_id = self.extract_video_id(news_url)
                if video_id:
                    logger.info(f"🎥 Vídeo da notícia original: {video_id}")
                    embed_code = self.generate_embed_code(video_id, "Vídeo da Notícia Original")
                    
                    # Inserir vídeo após o primeiro parágrafo
                    paragraphs = content.split('</p>')
                    if len(paragraphs) > 1:
                        paragraphs.insert(1, embed_code)
                        return '</p>'.join(paragraphs)
                    else:
                        return content + embed_code
            
            # Tentar extrair vídeo do título/descrição da notícia
            news_title = news_article.get('title', '')
            news_description = news_article.get('description', '')
            news_text = f"{news_title} {news_description}"
            
            video_id = self.extract_video_id(news_text)
            if video_id:
                logger.info(f"🎥 Vídeo encontrado na notícia original: {video_id}")
                embed_code = self.generate_embed_code(video_id, "Vídeo da Notícia Original")
                
                # Inserir vídeo após o primeiro parágrafo
                paragraphs = content.split('</p>')
                if len(paragraphs) > 1:
                    paragraphs.insert(1, embed_code)
                    return '</p>'.join(paragraphs)
                else:
                    return content + embed_code
        
        # 3. FALLBACK: Tentar extrair vídeo do conteúdo gerado
        video_id = self.extract_video_id(content)
        
        if video_id:
            logger.info(f"🎥 Vídeo extraído do conteúdo gerado: {video_id}")
            embed_code = self.generate_embed_code(video_id, "Vídeo Relacionado")
            
            # Inserir vídeo após o primeiro parágrafo
            paragraphs = content.split('</p>')
            if len(paragraphs) > 1:
                paragraphs.insert(1, embed_code)
                return '</p>'.join(paragraphs)
            else:
                return content + embed_code
        
        # 4. Se não encontrou vídeo na notícia original, não incluir nada
        logger.info("🎥 Nenhum vídeo encontrado na notícia original - não incluindo vídeo")
        return content
    
    def _should_include_related_video(self, topic, content):
        """
        Determina se deve incluir vídeo relacionado baseado na relevância
        """
        topic_lower = topic.lower()
        content_lower = content.lower()
        
        # Temas que SEMPRE se beneficiam de vídeo
        video_beneficial_topics = [
            'tutorial', 'como fazer', 'guia', 'dicas', 'passo a passo',
            'pescaria', 'pesca', 'caça', 'camping', 'trilha', 'escalada',
            'culinária', 'culinaria', 'receita', 'cozinha',
            'exercício', 'exercicio', 'treino', 'fitness',
            'arte', 'desenho', 'pintura', 'música', 'musica',
            'jardinagem', 'plantas', 'horta'
        ]
        
        # Verificar se o tema se beneficia de vídeo
        for keyword in video_beneficial_topics:
            if keyword in topic_lower:
                return True
        
        # Verificar se o conteúdo menciona vídeos
        if self.has_video_mention(content):
            return True
        
        # Verificar se o conteúdo é educativo/informativo
        educational_keywords = [
            'aprender', 'ensinar', 'demonstrar', 'mostrar', 'explicar',
            'técnica', 'tecnica', 'método', 'metodo', 'processo',
            'instrução', 'instrucao', 'orientação', 'orientacao'
        ]
        
        for keyword in educational_keywords:
            if keyword in content_lower:
                return True
        
        # Para temas muito específicos ou técnicos, não incluir vídeo genérico
        specific_topics = [
            'economia', 'política', 'politica', 'eleições', 'eleicoes',
            'inflação', 'inflacao', 'dólar', 'dolar', 'mercado',
            'governo', 'congresso', 'senado', 'câmara', 'camara'
        ]
        
        for keyword in specific_topics:
            if keyword in topic_lower:
                return False  # Não incluir vídeo genérico para temas políticos/econômicos
        
        return False  # Por padrão, não incluir vídeo genérico