# rb_ingestor/management/commands/improve_articles.py
"""
Comando para melhorar a qualidade dos artigos em termos de SEO
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.html import strip_tags
from datetime import timedelta
from rb_noticias.models import Noticia
import re

class Command(BaseCommand):
    help = "Melhora a qualidade dos artigos em termos de SEO"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=5, help="Número de artigos a melhorar")
        parser.add_argument("--hours", type=int, default=24, help="Horas para trás para buscar artigos")
        parser.add_argument("--dry-run", action="store_true", help="Apenas simula as melhorias")

    def handle(self, *args, **options):
        self.stdout.write("=== MELHORIA DE QUALIDADE DOS ARTIGOS ===")
        
        # Buscar artigos recentes
        recent_articles = Noticia.objects.filter(
            criado_em__gte=timezone.now() - timedelta(hours=options["hours"])
        ).order_by('-criado_em')[:options["limit"]]
        
        if not recent_articles:
            self.stdout.write("❌ Nenhum artigo encontrado")
            return
        
        self.stdout.write(f"📊 Analisando {len(recent_articles)} artigos para melhoria")
        
        improved_count = 0
        
        for i, article in enumerate(recent_articles, 1):
            self.stdout.write(f"\n--- MELHORANDO ARTIGO {i}: {article.titulo} ---")
            
            # Analisar artigo atual
            current_analysis = self._analyze_content(article.conteudo)
            self.stdout.write(f"📝 Palavras atuais: {current_analysis['word_count']}")
            self.stdout.write(f"🎯 Score SEO atual: {current_analysis['seo_score']}/100")
            
            # Verificar se precisa melhorar
            if current_analysis['word_count'] >= 600 and current_analysis['seo_score'] >= 80:
                self.stdout.write("✅ Artigo já está com boa qualidade")
                continue
            
            # Gerar conteúdo melhorado
            improved_content = self._improve_content(article.conteudo, article.titulo, article.categoria.nome if article.categoria else "geral")
            
            # Analisar conteúdo melhorado
            improved_analysis = self._analyze_content(improved_content)
            self.stdout.write(f"📝 Palavras melhoradas: {improved_analysis['word_count']}")
            self.stdout.write(f"🎯 Score SEO melhorado: {improved_analysis['seo_score']}/100")
            
            # Aplicar melhorias
            if not options["dry_run"]:
                article.conteudo = improved_content
                article.save()
                self.stdout.write("✅ Artigo melhorado e salvo!")
            else:
                self.stdout.write("🔍 Modo dry-run: Simulação apenas")
            
            improved_count += 1
        
        self.stdout.write(f"\n=== RESUMO ===")
        self.stdout.write(f"📊 Artigos analisados: {len(recent_articles)}")
        self.stdout.write(f"✅ Artigos melhorados: {improved_count}")
        
        if options["dry_run"]:
            self.stdout.write("🔍 Modo dry-run ativado - nenhuma alteração foi feita")

    def _analyze_content(self, content):
        """Analisa o conteúdo do artigo"""
        clean_content = strip_tags(content)
        words = clean_content.split()
        word_count = len(words)
        
        # Calcular score SEO básico
        seo_score = 0
        
        # Score por quantidade de palavras
        if word_count >= 800:
            seo_score += 40
        elif word_count >= 600:
            seo_score += 30
        elif word_count >= 400:
            seo_score += 20
        else:
            seo_score += 10
        
        # Score por estrutura
        if '<h2>' in content:
            seo_score += 20
        if '<h3>' in content:
            seo_score += 15
        if '<ul>' in content or '<ol>' in content:
            seo_score += 10
        if '<p>' in content:
            seo_score += 10
        
        # Score por elementos SEO
        if 'class="dek"' in content:
            seo_score += 5
        
        return {
            'word_count': word_count,
            'seo_score': min(seo_score, 100)
        }

    def _improve_content(self, content, title, category):
        """Melhora o conteúdo do artigo"""
        # Extrair informações básicas
        clean_content = strip_tags(content)
        current_words = len(clean_content.split())
        
        # Se já tem mais de 600 palavras, apenas otimizar estrutura
        if current_words >= 600:
            return self._optimize_structure(content, title, category)
        
        # Se tem menos de 600 palavras, expandir conteúdo
        return self._expand_content(content, title, category)

    def _optimize_structure(self, content, title, category):
        """Otimiza a estrutura do conteúdo"""
        # Adicionar mais subtítulos se necessário
        if content.count('<h2>') < 3:
            content = self._add_more_headings(content, title, category)
        
        # Adicionar mais listas se necessário
        if '<ul>' not in content and '<ol>' not in content:
            content = self._add_lists(content, category)
        
        # Melhorar densidade de palavras-chave
        content = self._improve_keyword_density(content, category)
        
        return content

    def _expand_content(self, content, title, category):
        """Expande o conteúdo do artigo"""
        # Adicionar seções adicionais
        additional_sections = self._generate_additional_sections(title, category)
        
        # Inserir antes da conclusão
        if '<h2>Conclusão</h2>' in content:
            content = content.replace('<h2>Conclusão</h2>', additional_sections + '<h2>Conclusão</h2>')
        else:
            content += additional_sections
        
        # Adicionar mais subtítulos
        content = self._add_more_headings(content, title, category)
        
        # Adicionar listas
        content = self._add_lists(content, category)
        
        # Melhorar densidade de palavras-chave
        content = self._improve_keyword_density(content, category)
        
        return content

    def _generate_additional_sections(self, title, category):
        """Gera seções adicionais para o artigo"""
        topic = title.lower()
        
        # Seções baseadas na categoria
        if "política" in category.lower():
            sections = """
<h2>Contexto Histórico</h2>
<p>Para entender melhor a situação atual, é importante analisar o contexto histórico que levou a essa situação. O Brasil tem passado por transformações significativas nos últimos anos, com mudanças políticas que impactaram diretamente a vida dos cidadãos brasileiros.</p>

<h2>Análise de Especialistas</h2>
<p>Especialistas em política brasileira destacam que esta situação reflete tendências mais amplas observadas em outros países. A análise comparativa mostra que o Brasil não está isolado nesse processo, mas enfrenta desafios únicos relacionados à sua história e cultura política.</p>

<h2>Impacto na Sociedade</h2>
<p>O impacto dessas mudanças na sociedade brasileira tem sido significativo. Desde as grandes metrópoles como São Paulo e Rio de Janeiro até as cidades do interior, é possível observar transformações que afetam o dia a dia das pessoas.</p>
"""
        elif "esportes" in category.lower():
            sections = """
<h2>História do Esporte no Brasil</h2>
<p>O Brasil tem uma rica tradição esportiva que remonta às primeiras décadas do século XX. Desde então, o país tem se destacado em diversas modalidades, criando uma cultura esportiva única que une pessoas de todas as classes sociais e regiões.</p>

<h2>Impacto Cultural</h2>
<p>O esporte no Brasil vai além da competição. Ele representa uma forma de expressão cultural, unindo comunidades e criando identidades regionais. Essa dimensão cultural do esporte é fundamental para entender sua importância na sociedade brasileira.</p>

<h2>Desenvolvimento e Infraestrutura</h2>
<p>Nos últimos anos, o Brasil tem investido significativamente na infraestrutura esportiva. Esses investimentos têm gerado resultados positivos, tanto para os atletas quanto para a população em geral, que tem acesso a melhores instalações esportivas.</p>
"""
        elif "tecnologia" in category.lower():
            sections = """
<h2>Evolução Tecnológica no Brasil</h2>
<p>O Brasil tem acompanhado a evolução tecnológica global, mas com características próprias. A adaptação de tecnologias internacionais ao contexto brasileiro tem gerado soluções inovadoras que atendem às necessidades específicas do país.</p>

<h2>Impacto na Economia</h2>
<p>A tecnologia tem se tornado um motor importante para o crescimento econômico brasileiro. Startups e empresas de tecnologia têm criado empregos e gerado riqueza, contribuindo para o desenvolvimento do país.</p>

<h2>Desafios e Oportunidades</h2>
<p>Embora existam desafios relacionados à infraestrutura e educação tecnológica, o Brasil tem grandes oportunidades de se destacar no cenário tecnológico global. A criatividade e o talento brasileiros são reconhecidos internacionalmente.</p>
"""
        else:
            sections = """
<h2>Contexto Nacional</h2>
<p>Esta questão tem relevância especial no contexto brasileiro, onde as particularidades locais influenciam diretamente os resultados observados. O Brasil, com sua diversidade regional e cultural, apresenta desafios e oportunidades únicos.</p>

<h2>Perspectivas Futuras</h2>
<p>As projeções para os próximos anos indicam que esta tendência deve se manter, com possíveis desenvolvimentos que podem trazer benefícios adicionais para o país. Os especialistas são cautelosamente otimistas quanto ao futuro.</p>

<h2>Comparação Internacional</h2>
<p>Quando comparamos a situação brasileira com outros países, é possível identificar padrões similares e diferenças importantes. Essa análise comparativa ajuda a entender melhor o contexto nacional e as possibilidades de melhoria.</p>
"""
        
        return sections

    def _add_more_headings(self, content, title, category):
        """Adiciona mais subtítulos ao conteúdo"""
        # Verificar se já tem subtítulos suficientes
        h2_count = content.count('<h2>')
        h3_count = content.count('<h3>')
        
        if h2_count >= 4 and h3_count >= 2:
            return content
        
        # Adicionar subtítulos H3 em seções existentes
        if '<h2>Análise Detalhada</h2>' in content:
            content = content.replace(
                '<h2>Análise Detalhada</h2>',
                '<h2>Análise Detalhada</h2>\n<h3>Aspectos Técnicos</h3>\n<p>Do ponto de vista técnico, esta questão apresenta características específicas que merecem atenção especial dos profissionais da área.</p>\n<h3>Implicações Práticas</h3>\n<p>As implicações práticas dessas mudanças são significativas e afetam diretamente a vida das pessoas no Brasil.</p>'
            )
        
        return content

    def _add_lists(self, content, category):
        """Adiciona listas ao conteúdo"""
        if '<ul>' in content or '<ol>' in content:
            return content
        
        # Adicionar lista de benefícios ou características
        list_content = """
<h3>Principais Características</h3>
<ul>
<li><strong>Relevância Nacional:</strong> Impacto direto na sociedade brasileira</li>
<li><strong>Sustentabilidade:</strong> Solução de longo prazo para os desafios atuais</li>
<li><strong>Inovação:</strong> Abordagem criativa e moderna</li>
<li><strong>Eficiência:</strong> Resultados comprovados e mensuráveis</li>
</ul>
"""
        
        # Inserir antes da conclusão
        if '<h2>Conclusão</h2>' in content:
            content = content.replace('<h2>Conclusão</h2>', list_content + '<h2>Conclusão</h2>')
        else:
            content += list_content
        
        return content

    def _improve_keyword_density(self, content, category):
        """Melhora a densidade de palavras-chave"""
        # Palavras-chave por categoria
        category_keywords = {
            "política": ["governo", "política", "brasil", "brasileiro", "nacional", "federal"],
            "esportes": ["esportes", "futebol", "brasil", "brasileiro", "competição", "atletismo"],
            "tecnologia": ["tecnologia", "digital", "brasil", "brasileiro", "inovação", "startup"],
            "economia": ["economia", "mercado", "brasil", "brasileiro", "investimento", "finanças"],
            "saúde": ["saúde", "medicina", "brasil", "brasileiro", "hospital", "tratamento"],
            "educação": ["educação", "escola", "brasil", "brasileiro", "universidade", "ensino"]
        }
        
        keywords = category_keywords.get(category.lower(), ["brasil", "brasileiro", "nacional"])
        
        # Adicionar palavras-chave naturalmente em parágrafos existentes
        for keyword in keywords:
            if keyword not in content.lower():
                # Adicionar em um parágrafo existente
                if '<p>' in content:
                    # Encontrar um parágrafo para adicionar a palavra-chave
                    paragraphs = content.split('<p>')
                    if len(paragraphs) > 1:
                        # Adicionar no segundo parágrafo
                        paragraphs[1] = paragraphs[1].replace(
                            '</p>',
                            f' Esta questão tem especial relevância no contexto {keyword} brasileiro.</p>',
                            1
                        )
                        content = '<p>'.join(paragraphs)
                        break
        
        return content
