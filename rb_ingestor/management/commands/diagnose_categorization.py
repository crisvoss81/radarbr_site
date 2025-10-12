# rb_ingestor/management/commands/diagnose_categorization.py
"""
Comando para diagnosticar problemas de categorização e formatação
"""
from django.core.management.base import BaseCommand
from rb_noticias.models import Noticia, Categoria
from collections import Counter

class Command(BaseCommand):
    help = "Diagnostica problemas de categorização e formatação"

    def handle(self, *args, **options):
        self.stdout.write("=== DIAGNÓSTICO DE CATEGORIZAÇÃO E FORMATAÇÃO ===")
        
        # Análise de categorização
        self.stdout.write("\n📊 ANÁLISE DE CATEGORIZAÇÃO:")
        noticias = Noticia.objects.all()
        
        if noticias.exists():
            # Contar por categoria
            categorias_count = Counter()
            for noticia in noticias:
                categoria_nome = noticia.categoria.nome if noticia.categoria else "Sem categoria"
                categorias_count[categoria_nome] += 1
            
            self.stdout.write("Distribuição por categoria:")
            for categoria, count in categorias_count.most_common():
                self.stdout.write(f"  {categoria}: {count} notícias")
            
            # Verificar se há problema de categorização
            if len(categorias_count) == 1:
                self.stdout.write("❌ PROBLEMA: Todas as notícias estão na mesma categoria!")
            elif categorias_count.most_common(1)[0][1] > len(noticias) * 0.8:
                self.stdout.write("⚠ ATENÇÃO: Mais de 80% das notícias estão na mesma categoria!")
        else:
            self.stdout.write("Nenhuma notícia encontrada")
        
        # Análise de formatação
        self.stdout.write("\n📝 ANÁLISE DE FORMATAÇÃO:")
        
        if noticias.exists():
            # Verificar padrões de subtítulos
            subtitulos_patterns = Counter()
            conteudos_identicos = 0
            
            for noticia in noticias[:10]:  # Analisar apenas as primeiras 10
                conteudo = noticia.conteudo
                
                # Extrair subtítulos (h2, h3)
                import re
                subtitulos = re.findall(r'<h[23][^>]*>(.*?)</h[23]>', conteudo)
                
                if subtitulos:
                    pattern = " | ".join(subtitulos[:3])  # Primeiros 3 subtítulos
                    subtitulos_patterns[pattern] += 1
                
                # Verificar se o conteúdo é muito genérico
                if "Análise completa e detalhada" in conteudo:
                    conteudos_identicos += 1
            
            self.stdout.write("Padrões de subtítulos encontrados:")
            for pattern, count in subtitulos_patterns.most_common(5):
                self.stdout.write(f"  {count}x: {pattern[:100]}...")
            
            if conteudos_identicos > 0:
                self.stdout.write(f"❌ PROBLEMA: {conteudos_identicos} notícias com conteúdo genérico!")
            
            if len(subtitulos_patterns) == 1:
                self.stdout.write("❌ PROBLEMA: Todas as notícias têm a mesma estrutura de subtítulos!")
        
        # Sugestões de correção
        self.stdout.write("\n🔧 SUGESTÕES DE CORREÇÃO:")
        self.stdout.write("1. Verificar função _detect_category nos comandos")
        self.stdout.write("2. Melhorar detecção de categoria baseada no conteúdo")
        self.stdout.write("3. Diversificar templates de conteúdo")
        self.stdout.write("4. Usar IA para gerar conteúdo mais específico")
        
        self.stdout.write("\n=== FIM DO DIAGNÓSTICO ===")
