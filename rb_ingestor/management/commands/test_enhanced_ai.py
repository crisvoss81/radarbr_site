# rb_ingestor/management/commands/test_enhanced_ai.py
"""
Comando para testar a IA melhorada
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.html import strip_tags

class Command(BaseCommand):
    help = "Testa a IA melhorada com diferentes tópicos"

    def add_arguments(self, parser):
        parser.add_argument("topic", type=str, help="Tópico para testar")
        parser.add_argument("--words", type=int, default=800, help="Número mínimo de palavras")
        parser.add_argument("--with-news", action="store_true", help="Simular contexto de notícia")

    def handle(self, *args, **options):
        topic = options["topic"]
        min_words = options["words"]
        
        self.stdout.write("=== TESTE IA MELHORADA ===")
        self.stdout.write(f"Tópico: {topic}")
        self.stdout.write(f"Mínimo de palavras: {min_words}")
        self.stdout.write(f"Executado em: {timezone.now()}")
        
        # Simular contexto de notícia se solicitado
        news_context = None
        if options["with_news"]:
            news_context = {
                'title': f'Notícia sobre {topic} ganha destaque',
                'description': f'Desenvolvimentos recentes relacionados a {topic} têm chamado atenção dos especialistas.',
                'source': 'CNN Brasil',
                'url': 'https://exemplo.com/noticia',
                'published_date': '2025-10-11'
            }
            self.stdout.write("📰 Simulando contexto de notícia")
        
        try:
            from rb_ingestor.ai_enhanced import generate_enhanced_article
            
            self.stdout.write("🤖 Gerando conteúdo com IA melhorada...")
            result = generate_enhanced_article(topic, news_context, min_words)
            
            if result:
                title = result.get('title', '')
                dek = result.get('dek', '')
                html = result.get('html', '')
                word_count = result.get('word_count', 0)
                quality_score = result.get('quality_score', 0)
                
                self.stdout.write("\n" + "="*50)
                self.stdout.write("📰 RESULTADO:")
                self.stdout.write("="*50)
                self.stdout.write(f"📝 Título: {title}")
                self.stdout.write(f"📄 Descrição: {dek}")
                self.stdout.write(f"📊 Palavras: {word_count}")
                self.stdout.write(f"⭐ Qualidade: {quality_score}%")
                
                # Mostrar preview do conteúdo
                clean_content = strip_tags(html)
                preview = clean_content[:300] + "..." if len(clean_content) > 300 else clean_content
                
                self.stdout.write(f"\n📖 Preview do conteúdo:")
                self.stdout.write("-" * 30)
                self.stdout.write(preview)
                self.stdout.write("-" * 30)
                
                # Análise de qualidade
                self.stdout.write(f"\n🔍 ANÁLISE DE QUALIDADE:")
                if quality_score >= 80:
                    self.stdout.write("✅ Excelente qualidade")
                elif quality_score >= 60:
                    self.stdout.write("✅ Boa qualidade")
                elif quality_score >= 40:
                    self.stdout.write("⚠️  Qualidade média")
                else:
                    self.stdout.write("❌ Qualidade baixa")
                
                # Verificar estrutura
                if '<h2>' in html:
                    self.stdout.write("✅ Estrutura com subtítulos H2")
                if '<h3>' in html:
                    self.stdout.write("✅ Estrutura com subtítulos H3")
                if '<ul>' in html or '<ol>' in html:
                    self.stdout.write("✅ Inclui listas")
                
            else:
                self.stdout.write("❌ Falha na geração de conteúdo")
                
        except Exception as e:
            self.stdout.write(f"❌ Erro: {e}")
            import traceback
            self.stdout.write(traceback.format_exc())
