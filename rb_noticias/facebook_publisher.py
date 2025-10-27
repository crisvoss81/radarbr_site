# rb_noticias/facebook_publisher.py
import logging
import facebook
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.html import strip_tags
import os

logger = logging.getLogger(__name__)

class FacebookPublisher:
    """Classe para publicar notícias automaticamente no Facebook"""
    
    def __init__(self):
        self.page_access_token = os.environ.get('FACEBOOK_PAGE_ACCESS_TOKEN')
        self.page_id = os.environ.get('FACEBOOK_PAGE_ID', '61582919670990')
        
        if not self.page_access_token:
            logger.warning("FACEBOOK_PAGE_ACCESS_TOKEN não configurado")
            self.graph = None
        else:
            try:
                self.graph = facebook.GraphAPI(self.page_access_token)
            except Exception as e:
                logger.error(f"Erro ao inicializar Facebook Graph API: {e}")
                self.graph = None
    
    def post_news(self, noticia):
        """
        Publica uma notícia no Facebook
        
        Args:
            noticia: Instância do modelo Noticia
        """
        if not self.graph:
            logger.error("Facebook Graph API não inicializado")
            return False
        
        try:
            # Construir URL completa da notícia
            site_url = os.environ.get('SITE_BASE_URL', 'https://radarbr.com.br')
            noticia_url = f"{site_url}{noticia.get_absolute_url()}"
            
            # Preparar mensagem
            # Limpar HTML do título
            titulo_limpo = strip_tags(noticia.titulo)
            
            # Criar descrição
            resumo = strip_tags(noticia.conteudo)[:200] + "..."
            
            # Montar mensagem
            mensagem = f"📰 {titulo_limpo}\n\n{resumo}\n\n👉 Leia mais: {noticia_url}"
            
            # Adicionar categoria se existir
            if noticia.categoria:
                mensagem += f"\n\n#{noticia.categoria.nome}"
            
            # Se tiver imagem, publicar com imagem
            if noticia.imagem:
                self._post_with_image(noticia, mensagem)
            else:
                self._post_text_only(mensagem)
            
            logger.info(f"Notícia publicada com sucesso no Facebook: {noticia.titulo}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao publicar notícia no Facebook: {e}")
            return False
    
    def _post_with_image(self, noticia, message):
        """Publica com imagem"""
        try:
            # Publicar com imagem (link)
            self.graph.put_object(
                parent_object=self.page_id,
                connection_name='feed',
                message=message,
                link=noticia.imagem
            )
        except Exception as e:
            logger.error(f"Erro ao publicar com imagem: {e}")
            # Fallback para publicação sem imagem
            self._post_text_only(message)
    
    def _post_text_only(self, message):
        """Publica apenas texto"""
        self.graph.put_object(
            parent_object=self.page_id,
            connection_name='feed',
            message=message
        )

