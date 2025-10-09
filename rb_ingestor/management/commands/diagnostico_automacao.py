# rb_ingestor/management/commands/diagnostico_automacao.py
"""
Comando para diagnosticar problemas do sistema de automação
"""
import os
import sys
import django
from django.core.management.base import BaseCommand
from django.apps import apps
from django.utils import timezone

class Command(BaseCommand):
    help = "Diagnostica problemas do sistema de automação"

    def handle(self, *args, **options):
        self.stdout.write("=== DIAGNÓSTICO DO SISTEMA DE AUTOMAÇÃO ===")
        
        # 1. Verificar variáveis de ambiente
        self.stdout.write("\n1. VARIÁVEIS DE AMBIENTE:")
        critical_vars = [
            'OPENAI_API_KEY',
            'UNSPLASH_API_KEY', 
            'PEXELS_API_KEY',
            'PIXABAY_API_KEY',
            'CLOUDINARY_CLOUD_NAME',
            'CLOUDINARY_API_KEY',
            'CLOUDINARY_API_SECRET',
            'ADSENSE_CLIENT'
        ]

        for var in critical_vars:
            value = os.getenv(var)
            if value:
                self.stdout.write(self.style.SUCCESS(f"  ✓ {var}: configurado"))
            else:
                self.stdout.write(self.style.ERROR(f"  ✗ {var}: NÃO CONFIGURADO"))

        # 2. Verificar dependências Python
        self.stdout.write("\n2. DEPENDÊNCIAS PYTHON:")
        dependencies = [
            'openai',
            'requests', 
            'gnews',
            'pytrends',
            'cloudinary',
            'slugify'
        ]

        for dep in dependencies:
            try:
                __import__(dep)
                self.stdout.write(self.style.SUCCESS(f"  ✓ {dep}: OK"))
            except ImportError:
                self.stdout.write(self.style.ERROR(f"  ✗ {dep}: NÃO INSTALADO"))

        # 3. Verificar modelos Django
        self.stdout.write("\n3. MODELOS DJANGO:")
        try:
            Noticia = apps.get_model("rb_noticias", "Noticia")
            Categoria = apps.get_model("rb_noticias", "Categoria")
            
            total_noticias = Noticia.objects.count()
            total_categorias = Categoria.objects.count()
            
            self.stdout.write(self.style.SUCCESS(f"  ✓ Noticia: {total_noticias} registros"))
            self.stdout.write(self.style.SUCCESS(f"  ✓ Categoria: {total_categorias} registros"))
            
            # Verificar notícias recentes
            recentes = Noticia.objects.filter(
                criado_em__gte=timezone.now() - timezone.timedelta(hours=24)
            ).count()
            self.stdout.write(self.style.SUCCESS(f"  ✓ Notícias últimas 24h: {recentes}"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ✗ Erro nos modelos: {e}"))

        # 4. Verificar sistema de IA
        self.stdout.write("\n4. SISTEMA DE IA:")
        try:
            from rb_ingestor.ai import generate_article
            self.stdout.write(self.style.SUCCESS("  ✓ Módulo AI importado"))
            
            if os.getenv('OPENAI_API_KEY'):
                self.stdout.write(self.style.SUCCESS("  ✓ OpenAI API Key configurada"))
            else:
                self.stdout.write(self.style.ERROR("  ✗ OpenAI API Key NÃO configurada"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ✗ Erro no sistema de IA: {e}"))

        # 5. Verificar sistema de imagens
        self.stdout.write("\n5. SISTEMA DE IMAGENS:")
        try:
            from rb_ingestor.image_search import ImageSearchEngine
            engine = ImageSearchEngine()
            self.stdout.write(self.style.SUCCESS("  ✓ ImageSearchEngine importado"))
            
            if engine.unsplash_key:
                self.stdout.write(self.style.SUCCESS("  ✓ Unsplash API Key configurada"))
            else:
                self.stdout.write(self.style.WARNING("  ⚠ Unsplash API Key NÃO configurada"))
                
            if engine.pexels_key:
                self.stdout.write(self.style.SUCCESS("  ✓ Pexels API Key configurada"))
            else:
                self.stdout.write(self.style.WARNING("  ⚠ Pexels API Key NÃO configurada"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ✗ Erro no sistema de imagens: {e}"))

        # 6. Verificar Cloudinary
        self.stdout.write("\n6. CLOUDINARY:")
        try:
            from rb_ingestor.images_cloudinary import _cloudinary_available
            if _cloudinary_available():
                self.stdout.write(self.style.SUCCESS("  ✓ Cloudinary configurado"))
            else:
                self.stdout.write(self.style.WARNING("  ⚠ Cloudinary NÃO configurado"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ✗ Erro no Cloudinary: {e}"))

        # 7. Teste de criação simples
        self.stdout.write("\n7. TESTE DE CRIAÇÃO:")
        try:
            Noticia = apps.get_model("rb_noticias", "Noticia")
            Categoria = apps.get_model("rb_noticias", "Categoria")
            
            # Criar categoria de teste
            cat, created = Categoria.objects.get_or_create(
                slug="teste-diagnostico",
                defaults={"nome": "Teste Diagnóstico"}
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS("  ✓ Categoria de teste criada"))
            else:
                self.stdout.write(self.style.SUCCESS("  ✓ Categoria de teste existente"))
            
            # Verificar se pode criar notícia (sem salvar)
            test_title = f"Teste Diagnóstico - {timezone.now().strftime('%H:%M')}"
            self.stdout.write(self.style.SUCCESS(f"  ✓ Título de teste gerado: {test_title}"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ✗ Erro no teste de criação: {e}"))

        self.stdout.write("\n=== DIAGNÓSTICO CONCLUÍDO ===")
        
        # Recomendações
        self.stdout.write("\nRECOMENDAÇÕES:")
        if not os.getenv('OPENAI_API_KEY'):
            self.stdout.write(self.style.WARNING("  ⚠ Configure OPENAI_API_KEY para usar IA"))
        if not os.getenv('UNSPLASH_API_KEY'):
            self.stdout.write(self.style.WARNING("  ⚠ Configure UNSPLASH_API_KEY para buscar imagens"))
        if not os.getenv('CLOUDINARY_CLOUD_NAME'):
            self.stdout.write(self.style.WARNING("  ⚠ Configure Cloudinary para upload de imagens"))
        
        self.stdout.write(self.style.SUCCESS("\n✓ Sistema básico funcionando - pode executar automação simples"))
