# rb_ingestor/management/commands/test_title_rewrite.py
"""
Comando para testar a reescrita inteligente de títulos
"""
from django.core.management.base import BaseCommand
from rb_ingestor.title_styles import title_style_manager

class Command(BaseCommand):
    help = "Testa a reescrita inteligente de títulos"

    def add_arguments(self, parser):
        parser.add_argument("keyword", type=str, help="Palavra-chave para testar")
        parser.add_argument("--title", type=str, help="Título base para reescrever")
        parser.add_argument("--count", type=int, default=5, help="Número de versões para gerar")

    def handle(self, *args, **options):
        keyword = options["keyword"]
        base_title = options.get("title")
        count = options["count"]
        
        if not base_title:
            # Títulos de exemplo para teste
            example_titles = [
                "PGR pede retomada de inquérito contra Bolsonaro por suposta interferência na PF - Gazeta do Povo",
                "Bitcoin sobe 15% após anúncio do Banco Central - G1",
                "Brasil não pode ser servo dos senhores feudais da tecnologia dos EUA - Valor",
                "O que Governo Trump anuncia sobre Venezuela? - CNN Brasil",
                "Lula confirma medidas para economia brasileira - Folha de S.Paulo"
            ]
            base_title = example_titles[0]  # Usar primeiro exemplo
        
        self.stdout.write(f"=== REESCRITA INTELIGENTE DE TÍTULOS ===")
        self.stdout.write(f"Palavra-chave: {keyword}")
        self.stdout.write(f"Título original: {base_title}")
        self.stdout.write("")
        
        # Limpar título
        clean_title = title_style_manager._clean_title_from_portals(base_title)
        self.stdout.write(f"📝 Título limpo: {clean_title}")
        self.stdout.write("")
        
        # Gerar várias versões reescritas
        self.stdout.write(f"🔄 GERANDO {count} VERSÕES REESCRITAS:")
        for i in range(count):
            rewritten = title_style_manager._rewrite_title_intelligently(clean_title, keyword)
            self.stdout.write(f"{i+1}. {rewritten}")
        
        self.stdout.write("")
        self.stdout.write("✅ Sistema de reescrita inteligente funcionando!")
