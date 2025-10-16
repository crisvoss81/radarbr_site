# rb_ingestor/management/commands/test_title_analysis.py
"""
Comando para testar a análise inteligente de títulos
"""
from django.core.management.base import BaseCommand
from rb_ingestor.title_styles import title_style_manager

class Command(BaseCommand):
    help = "Testa a análise inteligente de títulos"

    def add_arguments(self, parser):
        parser.add_argument("keyword", type=str, help="Palavra-chave para testar")
        parser.add_argument("--title", type=str, help="Título base para analisar")

    def handle(self, *args, **options):
        keyword = options["keyword"]
        base_title = options.get("title")
        
        if not base_title:
            # Títulos de exemplo para teste
            example_titles = [
                "PGR pede retomada de inquérito contra Bolsonaro por suposta interferência na PF - Gazeta do Povo",
                "Brasil não pode ser servo dos senhores feudais da tecnologia dos EUA, alerta Nobel de Economia | Valor",
                "O que Governo Trump anuncia sobre Venezuela? - CNN Brasil",
                "Bitcoin sobe 15% após anúncio do Banco Central - G1",
                "Lula confirma medidas para economia brasileira - Folha de S.Paulo"
            ]
            base_title = example_titles[0]  # Usar primeiro exemplo
        
        self.stdout.write(f"=== ANÁLISE INTELIGENTE DE TÍTULOS ===")
        self.stdout.write(f"Palavra-chave: {keyword}")
        self.stdout.write(f"Título base: {base_title}")
        self.stdout.write("")
        
        # Analisar título base
        analysis = title_style_manager._analyze_base_title(base_title, keyword)
        
        self.stdout.write("📊 ANÁLISE DO TÍTULO BASE:")
        self.stdout.write(f"- Título limpo: {analysis['clean_title']}")
        self.stdout.write(f"- Tem pergunta: {analysis['has_question']}")
        self.stdout.write(f"- Tem dois pontos: {analysis['has_colon']}")
        self.stdout.write(f"- Tem traço: {analysis['has_dash']}")
        self.stdout.write(f"- Entidades encontradas: {analysis['key_entities']}")
        self.stdout.write(f"- Ações encontradas: {analysis['key_actions']}")
        self.stdout.write(f"- Tópicos encontrados: {analysis['key_topics']}")
        self.stdout.write("")
        
        # Selecionar estilo apropriado
        style = title_style_manager._select_appropriate_style(analysis)
        style_info = title_style_manager.get_style_info(style)
        
        self.stdout.write(f"🎨 ESTILO SELECIONADO: {style_info['name']}")
        self.stdout.write(f"Descrição: {style_info['description']}")
        self.stdout.write("")
        
        # Gerar título contextual
        title = title_style_manager._generate_contextual_title(style, keyword, analysis)
        
        self.stdout.write(f"✅ TÍTULO GERADO: {title}")
        self.stdout.write("")
        
        # Testar com outros estilos para comparação
        self.stdout.write("🔄 COMPARAÇÃO COM OUTROS ESTILOS:")
        for style_name in ['pergunta_direta', 'analise_profunda', 'urgente_atual', 'impacto_social']:
            test_title = title_style_manager._generate_contextual_title(style_name, keyword, analysis)
            style_name_display = title_style_manager.get_style_info(style_name)['name']
            self.stdout.write(f"- [{style_name_display}] {test_title}")
