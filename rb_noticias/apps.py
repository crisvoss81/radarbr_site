from django.apps import AppConfig


class RbNoticiasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rb_noticias'
    
    def ready(self):
        import rb_noticias.signals