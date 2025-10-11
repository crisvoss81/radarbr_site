# rb_ingestor/management/commands/publish_trending_topics.py
"""
Comando para publicar notícias com os tópicos de tendência encontrados
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.html import strip_tags
from slugify import slugify
from datetime import datetime, timedelta
from rb_ingestor.trending_analyzer_real import RealTrendingAnalyzer
from django.apps import apps
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Publica notícias com os tópicos de tendência encontrados"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=5, help="Número de notícias a criar")
        parser.add_argument("--force", action="store_true", help="Força execução mesmo com notícias recentes")
        parser.add_argument("--debug", action="store_true", help="Modo debug")

    def handle(self, *args, **options):
        Noticia = apps.get_model("rb_noticias", "Noticia")
        Categoria = apps.get_model("rb_noticias", "Categoria")

        self.stdout.write("=== PUBLICAÇÃO DE TÓPICOS DE TENDÊNCIA ===")
        self.stdout.write(f"Executado em: {timezone.now()}")

        # Verificar se deve executar
        if not options["force"] and not self._should_execute(Noticia):
            self.stdout.write("PULANDO - muitas notícias recentes")
            return

        # Buscar tópicos de tendência
        analyzer = RealTrendingAnalyzer()
        topics = analyzer.get_cached_trends()
        
        # Limitar tópicos
        topics = topics[:options["limit"]]

        if not topics:
            self.stdout.write("❌ Nenhum tópico encontrado")
            return

        self.stdout.write(f"📊 Tópicos encontrados: {len(topics)}")

        # Publicar notícias
        created_count = self._publish_news_from_topics(topics, Noticia, Categoria, options["debug"])

        self.stdout.write(self.style.SUCCESS(f"✅ {created_count} notícias criadas com tópicos de tendência"))

        if created_count > 0:
            self._ping_sitemap()

    def _should_execute(self, Noticia):
        """Verifica se deve executar baseado em notícias recentes"""
        recent_count = Noticia.objects.filter(
            criado_em__gte=timezone.now() - timedelta(hours=2)
        ).count()
        return recent_count < 3

    def _publish_news_from_topics(self, topics, Noticia, Categoria, debug):
        """Publica notícias baseadas nos tópicos"""
        created_count = 0

        for i, topic_data in enumerate(topics):
            try:
                topic = topic_data["topic"]
                source = topic_data["source"]
                category = topic_data["category"]

                # Gerar título e conteúdo
                title, content = self._generate_content_from_topic(topic, category)
                
                # Obter categoria
                cat = self._get_category_for_topic(category, Categoria)
                
                # Criar slug
                slug = slugify(title)[:180]

                # Verificar duplicatas
                if not debug and self._check_duplicate(title, Noticia):
                    self.stdout.write(f"⚠ Pulando duplicata: {title}")
                    continue

                # Criar notícia
                noticia = Noticia.objects.create(
                    titulo=title,
                    slug=slug,
                    conteudo=content,
                    publicado_em=timezone.now(),
                    categoria=cat,
                    fonte_url=f"trending-{source}-{timezone.now().strftime('%Y%m%d-%H%M')}-{i}",
                    fonte_nome=f"RadarBR Trending ({source})",
                    status=1
                )

                # Adicionar imagem
                self._add_image(noticia, topic)

                self.stdout.write(f"✅ Criado: {title}")
                self.stdout.write(f"   📊 Fonte: {source}")
                self.stdout.write(f"   🏷️  Categoria: {cat.nome}")
                self.stdout.write(f"   🎯 Tópico: {topic}")

                created_count += 1

            except Exception as e:
                self.stdout.write(f"❌ Erro ao criar notícia: {e}")

        return created_count

    def _generate_content_from_topic(self, topic, category):
        """Gera conteúdo otimizado baseado no tópico e categoria"""
        try:
            # Tentar IA primeiro com instrução para artigo longo
            from rb_ingestor.ai import generate_article
            
            # Instrução específica para artigo longo
            long_article_prompt = f"""
            Crie um artigo completo e detalhado sobre "{topic}" com foco em SEO e relevância para o público brasileiro.
            
            REQUISITOS OBRIGATÓRIOS:
            - Mínimo de 800 palavras (ideal: 1000-1200 palavras)
            - Linguagem natural e conversacional
            - Estrutura com subtítulos H2 e H3
            - Incluir listas quando apropriado
            - Densidade de palavras-chave natural (1-3%)
            - Foco no contexto brasileiro
            - Tom informativo mas acessível
            
            ESTRUTURA SUGERIDA:
            1. Introdução envolvente
            2. Desenvolvimento principal (múltiplas seções)
            3. Análise detalhada
            4. Impacto no Brasil
            5. Perspectivas futuras
            6. Conclusão forte
            
            CATEGORIA: {category}
            
            Certifique-se de que o artigo seja substancial, informativo e otimizado para SEO.
            """
            
            ai_content = generate_article(long_article_prompt)

            if ai_content:
                title = strip_tags(ai_content.get("title", topic.title()))[:200]
                content = f'<p class="dek">{strip_tags(ai_content.get("dek", ""))[:220]}</p>\n{ai_content.get("html", "<p></p>")}'
                
                # Verificar se o conteúdo da IA tem pelo menos 800 palavras
                clean_content = strip_tags(content)
                word_count = len(clean_content.split())
                
                if word_count >= 800:
                    self.stdout.write(f"✅ IA gerou {word_count} palavras")
                    return title, content
                else:
                    self.stdout.write(f"⚠ IA gerou apenas {word_count} palavras, usando conteúdo SEO estendido")

        except Exception as e:
            self.stdout.write(f"⚠ IA falhou: {e}")

        # Conteúdo otimizado para SEO com mais palavras
        title = self._generate_seo_title(topic, category)
        content = self._generate_seo_content_extended(topic, category)

        return title, content

    def _generate_seo_title(self, topic, category):
        """Gera título otimizado para SEO baseado no tópico e categoria"""
        topic_lower = topic.lower()
        category_lower = category.lower()

        # Padrões específicos por categoria
        if "tecnologia" in category_lower:
            return f"{topic.title()}: Tendências e Inovações 2025"
        elif "economia" in category_lower:
            return f"{topic.title()}: Impacto na Economia Brasileira"
        elif "política" in category_lower:
            return f"{topic.title()}: Análise Política Completa"
        elif "esportes" in category_lower:
            return f"{topic.title()}: Últimas Notícias e Análises"
        elif "saúde" in category_lower:
            return f"{topic.title()}: Informações Importantes para Sua Saúde"
        elif "meio ambiente" in category_lower:
            return f"{topic.title()}: Sustentabilidade e Meio Ambiente"
        else:
            return f"{topic.title()}: Análise Completa e Atualizada"

    def _generate_seo_content(self, topic, category):
        """Gera conteúdo otimizado para SEO com mais palavras"""
        topic_lower = topic.lower()
        category_lower = category.lower()

        # Palavras-chave específicas por categoria
        category_keywords = {
            "tecnologia": ["tecnologia", "digital", "inovação", "startup", "brasil"],
            "economia": ["economia", "mercado", "investimento", "finanças", "brasil"],
            "política": ["política", "governo", "eleições", "democracia", "brasil"],
            "esportes": ["esportes", "futebol", "atletismo", "competição", "brasil"],
            "saúde": ["saúde", "medicina", "hospital", "tratamento", "brasil"],
            "meio ambiente": ["meio ambiente", "sustentabilidade", "natureza", "ecologia", "brasil"]
        }

        keywords = category_keywords.get(category_lower, ["brasil", "análise", "tendências"])

        content = f"""<p class="dek">Análise completa sobre {topic.lower()}, oferecendo informações atualizadas e insights valiosos para profissionais e interessados no tema.</p>

<h2>{topic.title()}: Análise Completa</h2>

<p>Uma análise detalhada sobre {topic.lower()} e seu impacto no cenário atual brasileiro. Este tema tem ganhado cada vez mais relevância no Brasil, merecendo atenção especial dos profissionais e interessados na área.</p>

<h3>Principais Desenvolvimentos</h3>

<p>Os desenvolvimentos recentes relacionados a {topic.lower()} indicam uma evolução significativa no cenário nacional. Especialistas destacam que este tema tem ganhado cada vez mais relevância no Brasil, com impactos diretos na sociedade brasileira.</p>

<ul>
<li><strong>Impacto Nacional:</strong> As mudanças observadas têm influência direta na economia brasileira</li>
<li><strong>Perspectivas Futuras:</strong> Projeções indicam crescimento sustentável nos próximos anos</li>
<li><strong>Relevância Social:</strong> O tema afeta diretamente a vida dos brasileiros</li>
</ul>

<h3>Análise Detalhada</h3>

<p>Os especialistas brasileiros destacam que {topic.lower()} tem ganhado cada vez mais relevância no cenário nacional. As mudanças observadas nos últimos meses indicam uma tendência consistente que merece atenção especial dos profissionais da área.</p>

<p>Esta evolução tem sido acompanhada de perto por analistas e pesquisadores que estudam o impacto dessas transformações na sociedade brasileira. Os dados mais recentes mostram uma evolução positiva em diversos indicadores relacionados ao tema.</p>

<h3>Contexto Histórico</h3>

<p>Para entender melhor a situação atual, é importante analisar o contexto histórico que levou a essa situação. O Brasil tem passado por transformações significativas nos últimos anos, com mudanças que impactaram diretamente a vida dos cidadãos brasileiros.</p>

<p>Esta questão tem relevância especial no contexto brasileiro, onde as particularidades locais influenciam diretamente os resultados observados. O Brasil, com sua diversidade regional e cultural, apresenta desafios e oportunidades únicos.</p>

<h3>Impacto na Sociedade Brasileira</h3>

<p>A população brasileira tem sentido diretamente os efeitos das transformações relacionadas a {topic.lower()}. Desde as grandes metrópoles como São Paulo e Rio de Janeiro até as cidades do interior, é possível observar mudanças significativas que afetam o dia a dia das pessoas.</p>

<p>Estas alterações têm sido recebidas de forma positiva pela maioria da população brasileira, que vê nas mudanças uma oportunidade de melhoria na qualidade de vida e desenvolvimento do país.</p>

<h3>Análise de Especialistas</h3>

<p>Especialistas na área destacam que esta situação reflete tendências mais amplas observadas em outros países. A análise comparativa mostra que o Brasil não está isolado nesse processo, mas enfrenta desafios únicos relacionados à sua história e cultura.</p>

<p>Os profissionais brasileiros têm desenvolvido soluções criativas e inovadoras para lidar com esses desafios, demonstrando a capacidade de adaptação e resiliência característica do povo brasileiro.</p>

<h3>Perspectivas para o Futuro</h3>

<p>As projeções para {topic.lower()} indicam que esta tendência deve se manter nos próximos anos, com possíveis desenvolvimentos que podem trazer benefícios adicionais para o Brasil. Os analistas são cautelosamente otimistas quanto ao futuro, destacando que o país tem todas as condições necessárias para se consolidar como uma referência na área.</p>

<p>As perspectivas futuras são promissoras, com indicadores que apontam para um crescimento sustentável e duradouro. Esta evolução positiva deve beneficiar não apenas os profissionais da área, mas toda a sociedade brasileira.</p>

<h3>Dados e Estatísticas</h3>

<p>Os números mais recentes sobre {topic.lower()} mostram uma evolução positiva em diversos indicadores relacionados ao tema. Esta melhoria tem sido observada de forma consistente ao longo dos últimos trimestres, demonstrando que não se trata de uma situação temporária, mas sim de uma tendência estrutural que deve perdurar.</p>

<p>As estatísticas oficiais confirmam essa tendência positiva, com dados que mostram crescimento em diversos setores relacionados ao tema. Esses números são fundamentais para entender a dimensão real das transformações em curso.</p>

<h3>Comparação Internacional</h3>

<p>Quando comparamos a situação brasileira com outros países, é possível identificar padrões similares e diferenças importantes. Essa análise comparativa ajuda a entender melhor o contexto nacional e as possibilidades de melhoria.</p>

<p>O Brasil tem se destacado internacionalmente em diversos aspectos relacionados a {topic.lower()}, recebendo reconhecimento de organizações internacionais e especialistas estrangeiros.</p>

<h3>Principais Características</h3>

<ul>
<li><strong>Relevância Nacional:</strong> Impacto direto na sociedade brasileira</li>
<li><strong>Sustentabilidade:</strong> Solução de longo prazo para os desafios atuais</li>
<li><strong>Inovação:</strong> Abordagem criativa e moderna</li>
<li><strong>Eficiência:</strong> Resultados comprovados e mensuráveis</li>
<li><strong>Adaptabilidade:</strong> Capacidade de se ajustar às necessidades locais</li>
</ul>

<h3>Conclusão</h3>

<p>Esta matéria sobre {topic.lower()} foi desenvolvida com base em informações atualizadas e análises de especialistas da área. O RadarBR continua acompanhando os desdobramentos desta notícia e manterá os leitores informados sobre novos desenvolvimentos relacionados ao tema.</p>

<p>O cenário atual é promissor e indica que o Brasil está no caminho certo para se consolidar como uma referência em {topic.lower()}. A continuidade das políticas públicas e o engajamento do setor privado serão fundamentais para manter o ritmo de crescimento observado.</p>

<p>Para mais informações sobre {topic.lower()} e outros assuntos relevantes para o Brasil, acompanhe nossas atualizações diárias e mantenha-se sempre bem informado sobre os temas que mais importam para o país.</p>"""

        return content

    def _generate_seo_content_extended(self, topic, category):
        """Gera conteúdo otimizado para SEO com mais de 800 palavras"""
        topic_lower = topic.lower()
        category_lower = category.lower()

        # Palavras-chave específicas por categoria
        category_keywords = {
            "tecnologia": ["tecnologia", "digital", "inovação", "startup", "brasil"],
            "economia": ["economia", "mercado", "investimento", "finanças", "brasil"],
            "política": ["política", "governo", "eleições", "democracia", "brasil"],
            "esportes": ["esportes", "futebol", "atletismo", "competição", "brasil"],
            "saúde": ["saúde", "medicina", "hospital", "tratamento", "brasil"],
            "meio ambiente": ["meio ambiente", "sustentabilidade", "natureza", "ecologia", "brasil"]
        }

        keywords = category_keywords.get(category_lower, ["brasil", "análise", "tendências"])

        content = f"""<p class="dek">Análise completa e detalhada sobre {topic.lower()}, oferecendo informações atualizadas e insights valiosos para profissionais e interessados no tema.</p>

<h2>{topic.title()}: Análise Completa e Detalhada</h2>

<p>Uma análise abrangente sobre {topic.lower()} e seu impacto no cenário atual brasileiro. Este tema tem ganhado cada vez mais relevância no Brasil, merecendo atenção especial dos profissionais e interessados na área. Neste artigo, exploraremos todos os aspectos relevantes dessa questão.</p>

<h3>Introdução ao Tema</h3>

<p>Para compreender completamente a importância de {topic.lower()}, é fundamental analisar seu contexto histórico e sua evolução ao longo do tempo. O Brasil, com sua rica diversidade cultural e geográfica, apresenta características únicas que influenciam diretamente como este tema se desenvolve em nosso país.</p>

<p>Os especialistas brasileiros destacam que {topic.lower()} tem ganhado cada vez mais relevância no cenário nacional. As mudanças observadas nos últimos meses indicam uma tendência consistente que merece atenção especial dos profissionais da área.</p>

<h3>Principais Desenvolvimentos Recentes</h3>

<p>Os desenvolvimentos recentes relacionados a {topic.lower()} indicam uma evolução significativa no cenário nacional. Especialistas destacam que este tema tem ganhado cada vez mais relevância no Brasil, com impactos diretos na sociedade brasileira.</p>

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

<p>A evolução histórica mostra que {topic.lower()} sempre esteve presente na sociedade brasileira, mas ganhou nova dimensão nos últimos anos. Essa transformação reflete mudanças mais amplas na economia e na sociedade.</p>

<h3>Análise Detalhada e Técnica</h3>

<p>Os especialistas brasileiros destacam que {topic.lower()} tem ganhado cada vez mais relevância no cenário nacional. As mudanças observadas nos últimos meses indicam uma tendência consistente que merece atenção especial dos profissionais da área.</p>

<p>Esta evolução tem sido acompanhada de perto por analistas e pesquisadores que estudam o impacto dessas transformações na sociedade brasileira. Os dados mais recentes mostram uma evolução positiva em diversos indicadores relacionados ao tema.</p>

<p>Do ponto de vista técnico, esta questão apresenta características específicas que merecem atenção especial dos profissionais da área. A implementação de novas tecnologias e metodologias tem revolucionado a forma como abordamos este tema.</p>

<h3>Impacto na Sociedade Brasileira</h3>

<p>A população brasileira tem sentido diretamente os efeitos das transformações relacionadas a {topic.lower()}. Desde as grandes metrópoles como São Paulo e Rio de Janeiro até as cidades do interior, é possível observar mudanças significativas que afetam o dia a dia das pessoas.</p>

<p>Estas alterações têm sido recebidas de forma positiva pela maioria da população brasileira, que vê nas mudanças uma oportunidade de melhoria na qualidade de vida e desenvolvimento do país.</p>

<p>O impacto social é especialmente relevante nas comunidades mais vulneráveis, onde essas transformações podem representar uma oportunidade de inclusão e desenvolvimento. Isso demonstra o potencial transformador desta questão para toda a sociedade brasileira.</p>

<h3>Análise de Especialistas e Pesquisadores</h3>

<p>Especialistas na área destacam que esta situação reflete tendências mais amplas observadas em outros países. A análise comparativa mostra que o Brasil não está isolado nesse processo, mas enfrenta desafios únicos relacionados à sua história e cultura.</p>

<p>Os profissionais brasileiros têm desenvolvido soluções criativas e inovadoras para lidar com esses desafios, demonstrando a capacidade de adaptação e resiliência característica do povo brasileiro.</p>

<p>As pesquisas acadêmicas mais recentes confirmam essa tendência positiva, com estudos que mostram resultados promissores em diversos aspectos relacionados ao tema. Esses dados são fundamentais para orientar políticas públicas e investimentos privados.</p>

<h3>Perspectivas para o Futuro</h3>

<p>As projeções para {topic.lower()} indicam que esta tendência deve se manter nos próximos anos, com possíveis desenvolvimentos que podem trazer benefícios adicionais para o Brasil. Os analistas são cautelosamente otimistas quanto ao futuro, destacando que o país tem todas as condições necessárias para se consolidar como uma referência na área.</p>

<p>As perspectivas futuras são promissoras, com indicadores que apontam para um crescimento sustentável e duradouro. Esta evolução positiva deve beneficiar não apenas os profissionais da área, mas toda a sociedade brasileira.</p>

<p>Os investimentos planejados para os próximos anos devem acelerar ainda mais essa tendência positiva, criando novas oportunidades e consolidando o Brasil como um player importante neste cenário.</p>

<h3>Dados, Estatísticas e Indicadores</h3>

<p>Os números mais recentes sobre {topic.lower()} mostram uma evolução positiva em diversos indicadores relacionados ao tema. Esta melhoria tem sido observada de forma consistente ao longo dos últimos trimestres, demonstrando que não se trata de uma situação temporária, mas sim de uma tendência estrutural que deve perdurar.</p>

<p>As estatísticas oficiais confirmam essa tendência positiva, com dados que mostram crescimento em diversos setores relacionados ao tema. Esses números são fundamentais para entender a dimensão real das transformações em curso.</p>

<p>Os indicadores de performance mostram melhorias significativas em diversos aspectos, desde a eficiência operacional até o impacto social. Esses resultados são fruto de investimentos estratégicos e da dedicação dos profissionais envolvidos.</p>

<h3>Comparação Internacional e Benchmarking</h3>

<p>Quando comparamos a situação brasileira com outros países, é possível identificar padrões similares e diferenças importantes. Essa análise comparativa ajuda a entender melhor o contexto nacional e as possibilidades de melhoria.</p>

<p>O Brasil tem se destacado internacionalmente em diversos aspectos relacionados a {topic.lower()}, recebendo reconhecimento de organizações internacionais e especialistas estrangeiros.</p>

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

<p>Esta matéria sobre {topic.lower()} foi desenvolvida com base em informações atualizadas e análises de especialistas da área. O RadarBR continua acompanhando os desdobramentos desta notícia e manterá os leitores informados sobre novos desenvolvimentos relacionados ao tema.</p>

<p>O cenário atual é promissor e indica que o Brasil está no caminho certo para se consolidar como uma referência em {topic.lower()}. A continuidade das políticas públicas e o engajamento do setor privado serão fundamentais para manter o ritmo de crescimento observado.</p>

<p>Para mais informações sobre {topic.lower()} e outros assuntos relevantes para o Brasil, acompanhe nossas atualizações diárias e mantenha-se sempre bem informado sobre os temas que mais importam para o país.</p>

<p>O futuro desta área no Brasil é promissor, e com os investimentos e políticas adequadas, podemos esperar resultados ainda melhores nos próximos anos. A sociedade brasileira tem muito a ganhar com o desenvolvimento contínuo desta questão.</p>"""

        return content

    def _get_category_for_topic(self, category_name, Categoria):
        """Obtém ou cria categoria baseada no nome"""
        if not category_name or category_name == "geral":
            category_name = "Brasil"

        cat = Categoria.objects.filter(nome=category_name).first()
        if cat:
            return cat

        # Criar nova categoria
        cat, created = Categoria.objects.get_or_create(
            slug=slugify(category_name)[:140],
            defaults={"nome": category_name}
        )
        return cat

    def _check_duplicate(self, title, Noticia):
        """Verifica se já existe notícia similar"""
        return Noticia.objects.filter(
            titulo__icontains=title[:20],
            criado_em__date=timezone.localdate()
        ).exists()

    def _add_image(self, noticia, topic):
        """Adiciona imagem à notícia"""
        try:
            from rb_ingestor.image_search import ImageSearchEngine

            search_engine = ImageSearchEngine()
            image_url = search_engine.search_image(
                noticia.titulo,
                noticia.conteudo,
                noticia.categoria.nome if noticia.categoria else "geral"
            )

            if image_url:
                noticia.imagem = image_url
                noticia.imagem_alt = f"Imagem relacionada a {topic}"
                noticia.imagem_credito = "Imagem gratuita"
                noticia.imagem_licenca = "CC"
                noticia.imagem_fonte_url = image_url
                noticia.save()

                self.stdout.write(f"   🖼️  Imagem adicionada")

        except Exception as e:
            self.stdout.write(f"   ⚠ Imagem não encontrada: {e}")

    def _ping_sitemap(self):
        """Faz ping do sitemap"""
        try:
            from core.utils import absolute_sitemap_url
            from rb_ingestor.ping import ping_search_engines
            
            sm_url = absolute_sitemap_url()
            res = ping_search_engines(sm_url)
            
            self.stdout.write(f"🔗 Ping sitemap: Google={'OK' if res['google'] else 'NOK'}; Bing={'OK' if res['bing'] else 'NOK'}")
            
        except Exception as e:
            self.stdout.write(f"⚠ Erro ao fazer ping do sitemap: {e}")
