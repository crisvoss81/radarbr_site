# rb_ingestor/management/commands/test_title_styles.py
"""
Comando para testar os estilos de título
"""
from django.core.management.base import BaseCommand
from rb_ingestor.title_styles import title_style_manager

class Command(BaseCommand):
    help = "Testa os estilos de título"

    def add_arguments(self, parser):
        parser.add_argument("keyword", type=str, help="Palavra-chave para testar")
        parser.add_argument("--count", type=int, default=5, help="Número de títulos para gerar")

    def handle(self, *args, **options):
        keyword = options["keyword"]
        count = options["count"]
        
        self.stdout.write(f"=== TESTE DE ESTILOS DE TÍTULO ===")
        self.stdout.write(f"Palavra-chave: {keyword}")
        self.stdout.write(f"Gerando {count} títulos diferentes:\n")
        
        for i in range(count):
            # Selecionar estilo aleatório
            style = title_style_manager.get_random_style()
            style_info = title_style_manager.get_style_info(style)
            
            # Gerar título
            title = title_style_manager.generate_title(style, keyword)
            
            self.stdout.write(f"{i+1}. [{style_info['name']}] {title}")
        
        self.stdout.write(f"\n=== TODOS OS ESTILOS DISPONÍVEIS ===")
        for style_name, style_info in title_style_manager.styles.items():
            self.stdout.write(f"- {style_info['name']}: {style_info['description']}")
            
        self.stdout.write(f"\n=== EXEMPLO COM TÍTULO BASE ===")
        base_title = f"Brasil anuncia medidas para {keyword}"
        smart_title = title_style_manager.generate_smart_title(keyword, base_title)
        self.stdout.write(f"Título base: {base_title}")
        self.stdout.write(f"Título inteligente: {smart_title}")
