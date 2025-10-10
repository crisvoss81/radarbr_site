# rb_ingestor/management/commands/teste_tamanho.py
"""
Comando para testar o tamanho padrão dos artigos
"""
from django.core.management.base import BaseCommand
from django.apps import apps
from django.utils import timezone
from slugify import slugify

class Command(BaseCommand):
    help = "Testa o tamanho padrão dos artigos"

    def handle(self, *args, **options):
        Noticia = apps.get_model("rb_noticias", "Noticia")
        Categoria = apps.get_model("rb_noticias", "Categoria")
        
        # Conteúdo com tamanho padrão expandido (700-1000 palavras)
        conteudo_teste = """<p class="dek">Startups brasileiras desenvolvem soluções inovadoras que chamam atenção mundialmente, posicionando o país como referência tecnológica na América Latina.</p>

Startups brasileiras estão desenvolvendo soluções inovadoras que chamam atenção internacionalmente, colocando o país em destaque no cenário tecnológico global.

### Principais Desenvolvimentos

As empresas nacionais têm apresentado resultados excepcionais em áreas como inteligência artificial, fintechs e sustentabilidade.

### Reconhecimento Mundial

Organizações internacionais têm destacado a qualidade e inovação das soluções desenvolvidas no Brasil.

## Análise Detalhada

Os especialistas destacam que este tema tem ganhado cada vez mais relevância no cenário nacional. As mudanças observadas nos últimos meses indicam uma tendência consistente que merece atenção especial. Esta evolução tem sido acompanhada de perto por analistas e pesquisadores que estudam o impacto dessas transformações na sociedade brasileira.

### Impacto na Sociedade Brasileira

A população brasileira tem sentido diretamente os efeitos dessas transformações. Desde as grandes metrópoles até as cidades do interior, é possível observar mudanças significativas que afetam o dia a dia das pessoas. Estas alterações têm sido recebidas de forma positiva pela maioria da população, que vê nas mudanças uma oportunidade de melhoria na qualidade de vida.

### Perspectivas para o Futuro

As projeções indicam que esta tendência deve se manter nos próximos anos, com possíveis desenvolvimentos que podem trazer benefícios adicionais para o país. Os analistas são cautelosamente otimistas quanto ao futuro, destacando que o Brasil tem todas as condições necessárias para se consolidar como uma referência na área.

## Dados e Estatísticas

Os números mais recentes mostram uma evolução positiva em diversos indicadores relacionados ao tema. Esta melhoria tem sido observada de forma consistente ao longo dos últimos trimestres, demonstrando que não se trata de uma situação temporária, mas sim de uma tendência estrutural que deve perdurar.

### Principais Indicadores

- Crescimento sustentável nos principais setores relacionados ao tema
- Melhoria significativa nos indicadores de qualidade e eficiência
- Aumento consistente da confiança dos investidores nacionais e internacionais
- Fortalecimento das instituições relacionadas ao setor
- Crescimento do número de empresas que atuam na área
- Aumento da demanda por profissionais especializados

### Comparação Internacional

Quando comparado com outros países da região, o Brasil tem se destacado positivamente. Esta posição de destaque tem sido reconhecida por organismos internacionais especializados, que destacam a qualidade das iniciativas implementadas no país. O Brasil tem conseguido superar expectativas e se posicionar como um exemplo a ser seguido por outras nações.

## Impacto Econômico

O impacto econômico dessas mudanças tem sido significativo, com aumento na geração de empregos e crescimento do PIB em setores relacionados. As empresas que investiram na área têm registrado resultados positivos, o que tem incentivado novos investimentos e parcerias estratégicas.

### Geração de Empregos

O setor tem sido responsável pela criação de milhares de novos postos de trabalho em todo o país. Profissionais de diversas áreas têm encontrado oportunidades de crescimento e desenvolvimento profissional, contribuindo para a redução do desemprego e melhoria da qualidade de vida das famílias brasileiras.

### Investimentos e Parcerias

O aumento da confiança dos investidores tem resultado em novos aportes financeiros e parcerias estratégicas entre empresas nacionais e internacionais. Estas parcerias têm contribuído para o desenvolvimento tecnológico e a modernização dos processos produtivos.

## Perguntas Frequentes

### Como isso afeta o brasileiro comum?

O impacto na vida das pessoas é direto e positivo. As mudanças têm trazido benefícios concretos que podem ser observados no dia a dia da população, incluindo melhorias na qualidade dos serviços, redução de custos e aumento da eficiência em diversos setores.

### O que esperar nos próximos meses?

As projeções indicam continuidade da tendência positiva, com possíveis desenvolvimentos adicionais que podem trazer ainda mais benefícios. Os especialistas esperam que novos avanços sejam anunciados nos próximos meses, consolidando ainda mais a posição do Brasil na área.

### Existem riscos envolvidos?

Como em qualquer processo de transformação, existem desafios a serem enfrentados, mas os especialistas consideram que os benefícios superam significativamente os riscos. O país tem demonstrado capacidade de adaptação e superação dos obstáculos encontrados.

### Como o governo tem apoiado essas iniciativas?

O governo federal tem implementado políticas públicas que incentivam o desenvolvimento da área, incluindo programas de financiamento, redução de impostos e facilitação de processos burocráticos. Estas medidas têm contribuído para acelerar o crescimento do setor.

## Conclusão

Esta matéria foi desenvolvida com base em informações atualizadas e análises de especialistas da área. O RadarBR continua acompanhando os desdobramentos desta notícia e manterá os leitores informados sobre novos desenvolvimentos.

O cenário atual é promissor e indica que o Brasil está no caminho certo para se consolidar como uma referência na área. A continuidade das políticas públicas e o engajamento do setor privado serão fundamentais para manter o ritmo de crescimento observado.

Para mais informações sobre este e outros assuntos relevantes, acompanhe nossas atualizações diárias e mantenha-se sempre bem informado sobre os temas que mais importam para o Brasil."""

        # Verificar tamanho
        palavras = len(conteudo_teste.split())
        caracteres = len(conteudo_teste)
        
        self.stdout.write("=== ANALISE DE TAMANHO PADRAO ===")
        self.stdout.write(f"Palavras: {palavras}")
        self.stdout.write(f"Caracteres: {caracteres}")
        self.stdout.write(f"Tamanho ideal: 700-1000 palavras")
        
        if palavras >= 700 and palavras <= 1000:
            self.stdout.write(self.style.SUCCESS("OK: Tamanho dentro do padrao ideal"))
        elif palavras < 700:
            self.stdout.write(self.style.WARNING(f"AVISO: {700-palavras} palavras abaixo do minimo"))
        else:
            self.stdout.write(self.style.WARNING(f"AVISO: {palavras-1000} palavras acima do maximo"))
        
        # Mostrar estrutura
        self.stdout.write("\n=== ESTRUTURA DO ARTIGO ===")
        linhas = conteudo_teste.split('\n')
        for linha in linhas:
            if linha.strip().startswith('##') or linha.strip().startswith('###'):
                self.stdout.write(f"  {linha.strip()}")
        
        self.stdout.write(f"\n=== RESUMO ===")
        self.stdout.write(f"Tamanho atual: {palavras} palavras")
        self.stdout.write(f"Padrao do site: 700-1000 palavras")
        self.stdout.write(f"Status: {'Dentro do padrao' if 700 <= palavras <= 1000 else 'Fora do padrao'}")
