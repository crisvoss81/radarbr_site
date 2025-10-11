# rb_ingestor/management/commands/test_long_article.py
"""
Comando para testar a criação de artigos longos
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.html import strip_tags
from slugify import slugify
from django.apps import apps

class Command(BaseCommand):
    help = "Testa a criação de artigos longos"

    def add_arguments(self, parser):
        parser.add_argument("--topic", type=str, default="Tecnologia no Brasil", help="Tópico para o artigo")
        parser.add_argument("--category", type=str, default="tecnologia", help="Categoria do artigo")

    def handle(self, *args, **options):
        Noticia = apps.get_model("rb_noticias", "Noticia")
        Categoria = apps.get_model("rb_noticias", "Categoria")

        self.stdout.write("=== TESTE DE ARTIGO LONGO ===")
        
        topic = options["topic"]
        category = options["category"]
        
        self.stdout.write(f"📝 Criando artigo sobre: {topic}")
        self.stdout.write(f"🏷️  Categoria: {category}")
        
        # Gerar conteúdo
        title, content = self._generate_long_content(topic, category)
        
        # Contar palavras
        clean_content = strip_tags(content)
        word_count = len(clean_content.split())
        
        self.stdout.write(f"📊 Palavras geradas: {word_count}")
        self.stdout.write(f"📏 Caracteres: {len(clean_content)}")
        
        if word_count >= 800:
            self.stdout.write("✅ Artigo atinge o objetivo de 800+ palavras!")
        else:
            self.stdout.write("❌ Artigo não atinge 800 palavras")
        
        # Criar notícia
        try:
            cat = Categoria.objects.filter(nome=category.title()).first()
            if not cat:
                cat, created = Categoria.objects.get_or_create(
                    slug=slugify(category)[:140],
                    defaults={"nome": category.title()}
                )
            
            slug = slugify(title)[:180]
            
            noticia = Noticia.objects.create(
                titulo=title,
                slug=slug,
                conteudo=content,
                publicado_em=timezone.now(),
                categoria=cat,
                fonte_url=f"test-long-article-{timezone.now().strftime('%Y%m%d-%H%M')}",
                fonte_nome="RadarBR Test Long Article",
                status=1
            )
            
            self.stdout.write(f"✅ Notícia criada: {title}")
            self.stdout.write(f"🔗 URL: /noticia/{slug}/")
            
        except Exception as e:
            self.stdout.write(f"❌ Erro ao criar notícia: {e}")

    def _generate_long_content(self, topic, category):
        """Gera conteúdo longo para teste"""
        topic_lower = topic.lower()
        category_lower = category.lower()

        title = f"{topic}: Análise Completa e Detalhada"

        content = f"""<p class="dek">Análise completa e detalhada sobre {topic_lower}, oferecendo informações atualizadas e insights valiosos para profissionais e interessados no tema.</p>

<h2>{topic}: Análise Completa e Detalhada</h2>

<p>Uma análise abrangente sobre {topic_lower} e seu impacto no cenário atual brasileiro. Este tema tem ganhado cada vez mais relevância no Brasil, merecendo atenção especial dos profissionais e interessados na área. Neste artigo, exploraremos todos os aspectos relevantes dessa questão.</p>

<h3>Introdução ao Tema</h3>

<p>Para compreender completamente a importância de {topic_lower}, é fundamental analisar seu contexto histórico e sua evolução ao longo do tempo. O Brasil, com sua rica diversidade cultural e geográfica, apresenta características únicas que influenciam diretamente como este tema se desenvolve em nosso país.</p>

<p>Os especialistas brasileiros destacam que {topic_lower} tem ganhado cada vez mais relevância no cenário nacional. As mudanças observadas nos últimos meses indicam uma tendência consistente que merece atenção especial dos profissionais da área.</p>

<h3>Principais Desenvolvimentos Recentes</h3>

<p>Os desenvolvimentos recentes relacionados a {topic_lower} indicam uma evolução significativa no cenário nacional. Especialistas destacam que este tema tem ganhado cada vez mais relevância no Brasil, com impactos diretos na sociedade brasileira.</p>

<p>Esta evolução tem sido acompanhada de perto por analistas e pesquisadores que estudam o impacto dessas transformações na sociedade brasileira. Os dados mais recentes mostram uma evolução positiva em diversos indicadores relacionados ao tema.</p>

<ul>
<li><strong>Impacto Nacional:</strong> As mudanças observadas têm influência direta na economia brasileira</li>
<li><strong>Perspectivas Futuras:</strong> Projeções indicam crescimento sustentável nos próximos anos</li>
<li><strong>Relevância Social:</strong> O tema afeta diretamente a vida dos brasileiros</li>
<li><strong>Inovação:</strong> Novas abordagens estão sendo desenvolvidas</li>
<li><strong>Sustentabilidade:</strong> Soluções de longo prazo estão sendo implementadas</li>
</ul>

<h3>Contexto Histórico e Evolução</h3>

<p>Para entender melhor a situação atual, é importante analisar o contexto histórico que levou a essa situação. O Brasil tem passado por transformações significativas nos últimos anos, com mudanças que impactaram diretamente a vida dos cidadãos brasileiros.</p>

<p>Esta questão tem relevância especial no contexto brasileiro, onde as particularidades locais influenciam diretamente os resultados observados. O Brasil, com sua diversidade regional e cultural, apresenta desafios e oportunidades únicos.</p>

<p>A evolução histórica mostra que {topic_lower} sempre esteve presente na sociedade brasileira, mas ganhou nova dimensão nos últimos anos. Essa transformação reflete mudanças mais amplas na economia e na sociedade.</p>

<h3>Análise Detalhada e Técnica</h3>

<p>Os especialistas brasileiros destacam que {topic_lower} tem ganhado cada vez mais relevância no cenário nacional. As mudanças observadas nos últimos meses indicam uma tendência consistente que merece atenção especial dos profissionais da área.</p>

<p>Esta evolução tem sido acompanhada de perto por analistas e pesquisadores que estudam o impacto dessas transformações na sociedade brasileira. Os dados mais recentes mostram uma evolução positiva em diversos indicadores relacionados ao tema.</p>

<p>Do ponto de vista técnico, esta questão apresenta características específicas que merecem atenção especial dos profissionais da área. A implementação de novas tecnologias e metodologias tem revolucionado a forma como abordamos este tema.</p>

<h3>Impacto na Sociedade Brasileira</h3>

<p>A população brasileira tem sentido diretamente os efeitos das transformações relacionadas a {topic_lower}. Desde as grandes metrópoles como São Paulo e Rio de Janeiro até as cidades do interior, é possível observar mudanças significativas que afetam o dia a dia das pessoas.</p>

<p>Estas alterações têm sido recebidas de forma positiva pela maioria da população brasileira, que vê nas mudanças uma oportunidade de melhoria na qualidade de vida e desenvolvimento do país.</p>

<p>O impacto social é especialmente relevante nas comunidades mais vulneráveis, onde essas transformações podem representar uma oportunidade de inclusão e desenvolvimento. Isso demonstra o potencial transformador desta questão para toda a sociedade brasileira.</p>

<h3>Análise de Especialistas e Pesquisadores</h3>

<p>Especialistas na área destacam que esta situação reflete tendências mais amplas observadas em outros países. A análise comparativa mostra que o Brasil não está isolado nesse processo, mas enfrenta desafios únicos relacionados à sua história e cultura.</p>

<p>Os profissionais brasileiros têm desenvolvido soluções criativas e inovadoras para lidar com esses desafios, demonstrando a capacidade de adaptação e resiliência característica do povo brasileiro.</p>

<p>As pesquisas acadêmicas mais recentes confirmam essa tendência positiva, com estudos que mostram resultados promissores em diversos aspectos relacionados ao tema. Esses dados são fundamentais para orientar políticas públicas e investimentos privados.</p>

<h3>Perspectivas para o Futuro</h3>

<p>As projeções para {topic_lower} indicam que esta tendência deve se manter nos próximos anos, com possíveis desenvolvimentos que podem trazer benefícios adicionais para o Brasil. Os analistas são cautelosamente otimistas quanto ao futuro, destacando que o país tem todas as condições necessárias para se consolidar como uma referência na área.</p>

<p>As perspectivas futuras são promissoras, com indicadores que apontam para um crescimento sustentável e duradouro. Esta evolução positiva deve beneficiar não apenas os profissionais da área, mas toda a sociedade brasileira.</p>

<p>Os investimentos planejados para os próximos anos devem acelerar ainda mais essa tendência positiva, criando novas oportunidades e consolidando o Brasil como um player importante neste cenário.</p>

<h3>Dados, Estatísticas e Indicadores</h3>

<p>Os números mais recentes sobre {topic_lower} mostram uma evolução positiva em diversos indicadores relacionados ao tema. Esta melhoria tem sido observada de forma consistente ao longo dos últimos trimestres, demonstrando que não se trata de uma situação temporária, mas sim de uma tendência estrutural que deve perdurar.</p>

<p>As estatísticas oficiais confirmam essa tendência positiva, com dados que mostram crescimento em diversos setores relacionados ao tema. Esses números são fundamentais para entender a dimensão real das transformações em curso.</p>

<p>Os indicadores de performance mostram melhorias significativas em diversos aspectos, desde a eficiência operacional até o impacto social. Esses resultados são fruto de investimentos estratégicos e da dedicação dos profissionais envolvidos.</p>

<h3>Comparação Internacional e Benchmarking</h3>

<p>Quando comparamos a situação brasileira com outros países, é possível identificar padrões similares e diferenças importantes. Essa análise comparativa ajuda a entender melhor o contexto nacional e as possibilidades de melhoria.</p>

<p>O Brasil tem se destacado internacionalmente em diversos aspectos relacionados a {topic_lower}, recebendo reconhecimento de organizações internacionais e especialistas estrangeiros.</p>

<p>Os países que mais se destacam nesta área têm características similares ao Brasil, o que sugere que estamos no caminho certo. No entanto, ainda há muito espaço para crescimento e melhoria.</p>

<h3>Desafios e Oportunidades</h3>

<p>Embora os resultados sejam positivos, ainda existem desafios significativos que precisam ser enfrentados. A identificação desses desafios é fundamental para o desenvolvimento de estratégias eficazes.</p>

<p>As oportunidades, por outro lado, são abundantes e promissoras. O Brasil tem todas as condições necessárias para se tornar uma referência mundial nesta área, desde recursos naturais até capital humano qualificado.</p>

<h3>Principais Características e Benefícios</h3>

<ul>
<li><strong>Relevância Nacional:</strong> Impacto direto na sociedade brasileira</li>
<li><strong>Sustentabilidade:</strong> Solução de longo prazo para os desafios atuais</li>
<li><strong>Inovação:</strong> Abordagem criativa e moderna</li>
<li><strong>Eficiência:</strong> Resultados comprovados e mensuráveis</li>
<li><strong>Adaptabilidade:</strong> Capacidade de se ajustar às necessidades locais</li>
<li><strong>Escalabilidade:</strong> Potencial para crescimento e expansão</li>
<li><strong>Impacto Social:</strong> Benefícios para toda a comunidade</li>
</ul>

<h3>Recomendações e Próximos Passos</h3>

<p>Com base na análise apresentada, é possível identificar algumas recomendações importantes para o desenvolvimento futuro desta área. Essas recomendações são fundamentadas em dados concretos e na experiência de especialistas.</p>

<p>O primeiro passo é continuar investindo em pesquisa e desenvolvimento, garantindo que o Brasil mantenha sua posição de liderança. Além disso, é importante focar na formação de profissionais qualificados.</p>

<h3>Conclusão</h3>

<p>Esta matéria sobre {topic_lower} foi desenvolvida com base em informações atualizadas e análises de especialistas da área. O RadarBR continua acompanhando os desdobramentos desta notícia e manterá os leitores informados sobre novos desenvolvimentos relacionados ao tema.</p>

<p>O cenário atual é promissor e indica que o Brasil está no caminho certo para se consolidar como uma referência em {topic_lower}. A continuidade das políticas públicas e o engajamento do setor privado serão fundamentais para manter o ritmo de crescimento observado.</p>

<p>Para mais informações sobre {topic_lower} e outros assuntos relevantes para o Brasil, acompanhe nossas atualizações diárias e mantenha-se sempre bem informado sobre os temas que mais importam para o país.</p>

<p>O futuro desta área no Brasil é promissor, e com os investimentos e políticas adequadas, podemos esperar resultados ainda melhores nos próximos anos. A sociedade brasileira tem muito a ganhar com o desenvolvimento contínuo desta questão.</p>"""

        return title, content
