# rb_noticias/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Noticia
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Noticia)
def publish_news_to_facebook(sender, instance, created, **kwargs):
    """
    Signal que detecta quando uma notícia é criada ou atualizada
    e publica automaticamente no Facebook
    """
    # Só publica se a notícia estiver publicada
    if instance.status != Noticia.Status.PUBLICADO:
        return
    
    try:
        from .facebook_publisher import FacebookPublisher
        
        facebook_publisher = FacebookPublisher()
        
        # Se foi criada agora (nova publicação)
        if created:
            logger.info(f"Publicando nova notícia no Facebook: {instance.titulo}")
            facebook_publisher.post_news(instance)
        # Se foi atualizada e mudou de status para publicado
        elif hasattr(instance, '_previous_status') and instance._previous_status != Noticia.Status.PUBLICADO:
            logger.info(f"Publicando notícia atualizada no Facebook: {instance.titulo}")
            facebook_publisher.post_news(instance)
            
    except ImportError:
        logger.warning("Facebook publisher não disponível. Verifique se as credenciais estão configuradas.")
    except Exception as e:
        logger.error(f"Erro ao publicar no Facebook: {e}")

