# rb_ingestor/management/commands/analyze_articles.py
"""
Comando para analisar a qualidade dos artigos em termos de SEO
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.utils.html import strip_tags
import re
from rb_noticias.models import Noticia

class Command(BaseCommand):
    help = "Analisa a qualidade dos artigos em termos de SEO"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=5, help="Número de artigos a analisar")
        parser.add_argument("--hours", type=int, default=24, help="Horas para trás para buscar artigos")

    def handle(self, *args, **options):
        self.stdout.write("=== ANÁLISE DE QUALIDADE DOS ARTIGOS ===")
        
        # Buscar artigos recentes
        recent_articles = Noticia.objects.filter(
            criado_em__gte=timezone.now() - timedelta(hours=options["hours"])
        ).order_by('-criado_em')[:options["limit"]]
        
        if not recent_articles:
            self.stdout.write("❌ Nenhum artigo encontrado")
            return
        
        self.stdout.write(f"📊 Analisando {len(recent_articles)} artigos recentes")
        
        total_words = 0
        total_chars = 0
        seo_scores = []
        
        for i, article in enumerate(recent_articles, 1):
            self.stdout.write(f"\n--- ARTIGO {i}: {article.titulo} ---")
            self.stdout.write(f"📅 Data: {article.criado_em}")
            self.stdout.write(f"🏷️  Categoria: {article.categoria.nome if article.categoria else 'Sem categoria'}")
            self.stdout.write(f"🔗 Fonte: {article.fonte_nome}")
            
            # Análise de conteúdo
            content_analysis = self._analyze_content(article.conteudo)
            
            self.stdout.write(f"📝 Palavras: {content_analysis['word_count']}")
            self.stdout.write(f"📏 Caracteres: {content_analysis['char_count']}")
            self.stdout.write(f"📊 Densidade de palavras-chave: {content_analysis['keyword_density']:.2f}%")
            self.stdout.write(f"🎯 Score SEO: {content_analysis['seo_score']}/100")
            
            # Preview do conteúdo
            preview = strip_tags(article.conteudo)[:200]
            self.stdout.write(f"👁️  Preview: {preview}...")
            
            total_words += content_analysis['word_count']
            total_chars += content_analysis['char_count']
            seo_scores.append(content_analysis['seo_score'])
        
        # Estatísticas gerais
        self.stdout.write(f"\n=== ESTATÍSTICAS GERAIS ===")
        self.stdout.write(f"📊 Total de artigos analisados: {len(recent_articles)}")
        self.stdout.write(f"📝 Média de palavras: {total_words // len(recent_articles)}")
        self.stdout.write(f"📏 Média de caracteres: {total_chars // len(recent_articles)}")
        self.stdout.write(f"🎯 Score SEO médio: {sum(seo_scores) / len(seo_scores):.1f}/100")
        
        # Análise de qualidade
        self._analyze_quality(total_words // len(recent_articles), sum(seo_scores) / len(seo_scores))

    def _analyze_content(self, content):
        """Analisa o conteúdo do artigo"""
        # Remover HTML tags
        clean_content = strip_tags(content)
        
        # Contar palavras e caracteres
        words = clean_content.split()
        word_count = len(words)
        char_count = len(clean_content)
        
        # Calcular densidade de palavras-chave
        keyword_density = self._calculate_keyword_density(words)
        
        # Calcular score SEO
        seo_score = self._calculate_seo_score(word_count, char_count, keyword_density, content)
        
        return {
            'word_count': word_count,
            'char_count': char_count,
            'keyword_density': keyword_density,
            'seo_score': seo_score
        }

    def _calculate_keyword_density(self, words):
        """Calcula densidade de palavras-chave"""
        if not words:
            return 0
        
        # Palavras-chave importantes para SEO
        important_keywords = [
            'brasil', 'brasileiro', 'brasileira', 'nacional', 'federal',
            'governo', 'política', 'economia', 'tecnologia', 'esportes',
            'saúde', 'educação', 'meio ambiente', 'sustentabilidade'
        ]
        
        keyword_count = 0
        for word in words:
            if word.lower() in important_keywords:
                keyword_count += 1
        
        return (keyword_count / len(words)) * 100

    def _calculate_seo_score(self, word_count, char_count, keyword_density, content):
        """Calcula score SEO baseado em múltiplos fatores"""
        score = 0
        
        # Score por quantidade de palavras (ideal: 800-1500 palavras)
        if 800 <= word_count <= 1500:
            score += 25
        elif 600 <= word_count < 800:
            score += 20
        elif 400 <= word_count < 600:
            score += 15
        elif 200 <= word_count < 400:
            score += 10
        else:
            score += 5
        
        # Score por densidade de palavras-chave (ideal: 1-3%)
        if 1 <= keyword_density <= 3:
            score += 20
        elif 0.5 <= keyword_density < 1:
            score += 15
        elif 3 < keyword_density <= 5:
            score += 10
        else:
            score += 5
        
        # Score por estrutura HTML
        if '<h2>' in content:
            score += 10
        if '<h3>' in content:
            score += 10
        if '<ul>' in content or '<ol>' in content:
            score += 10
        if '<p>' in content:
            score += 10
        
        # Score por elementos SEO
        if 'class="dek"' in content:
            score += 5
        if '<strong>' in content:
            score += 5
        if '<em>' in content:
            score += 5
        
        # Score por linguagem natural (verificar repetições)
        if self._check_natural_language(content):
            score += 10
        
        return min(score, 100)  # Máximo 100

    def _check_natural_language(self, content):
        """Verifica se a linguagem é natural"""
        clean_content = strip_tags(content).lower()
        
        # Verificar repetições excessivas
        words = clean_content.split()
        if len(words) < 100:
            return True
        
        # Verificar se há repetições excessivas de palavras
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Ignorar palavras muito curtas
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Se alguma palavra aparece mais de 5% do tempo, pode ser repetitiva
        max_freq = max(word_freq.values()) if word_freq else 0
        if max_freq > len(words) * 0.05:
            return False
        
        return True

    def _analyze_quality(self, avg_words, avg_seo_score):
        """Analisa a qualidade geral"""
        self.stdout.write(f"\n=== ANÁLISE DE QUALIDADE ===")
        
        # Análise de quantidade de palavras
        if avg_words >= 800:
            self.stdout.write("✅ Quantidade de palavras: EXCELENTE (800+ palavras)")
        elif avg_words >= 600:
            self.stdout.write("✅ Quantidade de palavras: BOA (600-800 palavras)")
        elif avg_words >= 400:
            self.stdout.write("⚠️  Quantidade de palavras: REGULAR (400-600 palavras)")
        else:
            self.stdout.write("❌ Quantidade de palavras: BAIXA (<400 palavras)")
        
        # Análise de score SEO
        if avg_seo_score >= 80:
            self.stdout.write("✅ Score SEO: EXCELENTE (80+ pontos)")
        elif avg_seo_score >= 60:
            self.stdout.write("✅ Score SEO: BOA (60-80 pontos)")
        elif avg_seo_score >= 40:
            self.stdout.write("⚠️  Score SEO: REGULAR (40-60 pontos)")
        else:
            self.stdout.write("❌ Score SEO: BAIXA (<40 pontos)")
        
        # Recomendações
        self.stdout.write(f"\n=== RECOMENDAÇÕES ===")
        
        if avg_words < 600:
            self.stdout.write("📝 RECOMENDAÇÃO: Aumentar quantidade de palavras para melhor SEO")
        
        if avg_seo_score < 60:
            self.stdout.write("🎯 RECOMENDAÇÃO: Melhorar estrutura e densidade de palavras-chave")
        
        if avg_words >= 600 and avg_seo_score >= 60:
            self.stdout.write("🎉 PARABÉNS: Artigos com boa qualidade para SEO!")
        
        # Dicas específicas
        self.stdout.write(f"\n=== DICAS PARA MELHORAR SEO ===")
        self.stdout.write("1. 📝 Use subtítulos (H2, H3) para estrutura")
        self.stdout.write("2. 🎯 Inclua palavras-chave relevantes naturalmente")
        self.stdout.write("3. 📊 Use listas e formatação para melhor leitura")
        self.stdout.write("4. 🔗 Adicione links internos quando possível")
        self.stdout.write("5. 📱 Escreva para humanos, não apenas para SEO")
