# rb_ingestor/management/commands/publish_topic.py
"""
Comando completo para publicar artigo com tópico especificado manualmente
Seguindo toda a lógica do sistema RadarBR
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.html import strip_tags
from slugify import slugify
from django.apps import apps
import logging
import random

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Publica artigo com tópico especificado manualmente seguindo toda a lógica do sistema"

    def add_arguments(self, parser):
        parser.add_argument("topic", type=str, help="Tópico para o artigo")
        parser.add_argument("--category", type=str, help="Categoria específica (opcional)")
        parser.add_argument("--title", type=str, help="Título personalizado (opcional)")
        parser.add_argument("--force", action="store_true", help="Força publicação mesmo com duplicatas")
        parser.add_argument("--debug", action="store_true", help="Modo debug")
        parser.add_argument("--dry-run", action="store_true", help="Apenas simula, não publica")
        parser.add_argument("--words", type=int, default=800, help="Número mínimo de palavras (padrão: 800)")

    def handle(self, *args, **options):
        Noticia = apps.get_model("rb_noticias", "Noticia")
        Categoria = apps.get_model("rb_noticias", "Categoria")

        self.stdout.write("=== PUBLICAÇÃO MANUAL DE TÓPICO ===")
        self.stdout.write(f"Executado em: {timezone.now()}")
        
        topic = options["topic"]
        category = options.get("category")
        custom_title = options.get("title")
        min_words = options["words"]
        
        self.stdout.write(f"📝 Tópico: {topic}")
        if category:
            self.stdout.write(f"🏷️  Categoria especificada: {category}")
        if custom_title:
            self.stdout.write(f"📰 Título personalizado: {custom_title}")
        self.stdout.write(f"📊 Mínimo de palavras: {min_words}")

        # Verificar duplicatas se não forçar
        if not options["force"] and not options["dry_run"]:
            if self._check_duplicate(topic, Noticia):
                self.stdout.write("⚠ Tópico similar já existe. Use --force para publicar mesmo assim.")
                return

        # Gerar título e conteúdo
        if custom_title:
            title = custom_title
        else:
            title = self._generate_title(topic, category)
        
        content = self._generate_content(topic, category, min_words)
        
        # Verificar qualidade do conteúdo
        word_count = len(strip_tags(content).split())
        self.stdout.write(f"📊 Palavras geradas: {word_count}")
        
        if word_count < min_words:
            self.stdout.write(f"⚠ Conteúdo com menos de {min_words} palavras, expandindo...")
            content = self._expand_content(content, topic, category, min_words)
            word_count = len(strip_tags(content).split())
            self.stdout.write(f"📊 Palavras após expansão: {word_count}")

        # Obter categoria
        cat = self._get_category(topic, category, Categoria)
        
        # Criar slug único
        timestamp = timezone.now().strftime('%Y%m%d-%H%M%S')
        slug = slugify(f"{title}-{timestamp}")[:180]

        if options["dry_run"]:
            self.stdout.write("🔍 MODO DRY-RUN - Simulação apenas")
            self.stdout.write(f"📰 Título: {title}")
            self.stdout.write(f"🏷️  Categoria: {cat.nome}")
            self.stdout.write(f"🔗 Slug: {slug}")
            self.stdout.write(f"📊 Palavras: {word_count}")
            self.stdout.write(f"📏 Caracteres: {len(strip_tags(content))}")
            return

        # Criar notícia
        try:
            noticia = Noticia.objects.create(
                titulo=title,
                slug=slug,
                conteudo=content,
                publicado_em=timezone.now(),
                categoria=cat,
                fonte_url=f"manual-topic-{timestamp}-{topic[:20].replace(' ', '-')}",
                fonte_nome="RadarBR Manual Topic",
                status=1
            )

            # Adicionar imagem
            self._add_image(noticia, topic)

            self.stdout.write(self.style.SUCCESS(f"✅ Artigo publicado com sucesso!"))
            self.stdout.write(f"📰 Título: {title}")
            self.stdout.write(f"🏷️  Categoria: {cat.nome}")
            self.stdout.write(f"🔗 URL: /noticia/{slug}/")
            self.stdout.write(f"📊 Palavras: {word_count}")
            self.stdout.write(f"📏 Caracteres: {len(strip_tags(content))}")

            # Ping sitemap
            self._ping_sitemap()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro ao publicar: {e}"))

    def _check_duplicate(self, topic, Noticia):
        """Verifica se já existe notícia similar"""
        return Noticia.objects.filter(
            titulo__icontains=topic[:20],
            criado_em__date=timezone.localdate()
        ).exists()

    def _generate_title(self, topic, category):
        """Gera título otimizado para SEO"""
        topic_lower = topic.lower()
        
        if category:
            category_lower = category.lower()
        else:
            category_lower = self._detect_category(topic_lower)

        # Padrões específicos por categoria
        title_patterns = {
            "tecnologia": [
                f"{topic.title()}: Tendências e Inovações 2025",
                f"{topic.title()}: Revolução Digital no Brasil",
                f"{topic.title()}: Futuro da Tecnologia Brasileira"
            ],
            "economia": [
                f"{topic.title()}: Impacto na Economia Brasileira",
                f"{topic.title()}: Análise Econômica Completa",
                f"{topic.title()}: Mercado e Investimentos"
            ],
            "política": [
                f"{topic.title()}: Análise Política Completa",
                f"{topic.title()}: Cenário Político Nacional",
                f"{topic.title()}: Democracia e Governança"
            ],
            "esportes": [
                f"{topic.title()}: Últimas Notícias e Análises",
                f"{topic.title()}: Paixão Nacional",
                f"{topic.title()}: Esportes no Brasil"
            ],
            "saúde": [
                f"{topic.title()}: Informações Importantes para Sua Saúde",
                f"{topic.title()}: Bem-estar e Qualidade de Vida",
                f"{topic.title()}: Saúde Pública Brasileira"
            ],
            "meio ambiente": [
                f"{topic.title()}: Sustentabilidade e Meio Ambiente",
                f"{topic.title()}: Preservação Ambiental",
                f"{topic.title()}: Futuro Sustentável"
            ]
        }
        
        patterns = title_patterns.get(category_lower, [
            f"{topic.title()}: Análise Completa e Atualizada",
            f"{topic.title()}: Tendências e Perspectivas",
            f"{topic.title()}: Guia Definitivo"
        ])
        
        return random.choice(patterns)

    def _detect_category(self, topic_lower):
        """Detecta categoria baseada no tópico"""
        category_keywords = {
            "tecnologia": ["tecnologia", "digital", "ia", "inteligência artificial", "chatgpt", "app", "software", "blockchain", "crypto", "bitcoin"],
            "economia": ["economia", "mercado", "inflação", "dólar", "real", "investimento", "finanças", "banco", "crédito"],
            "política": ["política", "governo", "eleições", "presidente", "lula", "bolsonaro", "congresso", "ministro"],
            "esportes": ["esportes", "futebol", "copa", "mundial", "brasileirão", "atletismo", "jogos", "competição"],
            "saúde": ["saúde", "medicina", "hospital", "vacina", "covid", "coronavírus", "tratamento", "médico"],
            "meio ambiente": ["meio ambiente", "sustentabilidade", "natureza", "clima", "ecologia", "verde", "energia"]
        }
        
        for category, keywords in category_keywords.items():
            if any(kw in topic_lower for kw in keywords):
                return category
        
        return "geral"

    def _generate_content(self, topic, category, min_words):
        """Gera conteúdo otimizado para SEO"""
        try:
            # Tentar IA primeiro com instrução para artigo longo
            from rb_ingestor.ai import generate_article
            
            # Instrução específica para artigo longo
            long_article_prompt = f"""
            Crie um artigo completo e detalhado sobre "{topic}" com foco em SEO e relevância para o público brasileiro.
            
            REQUISITOS OBRIGATÓRIOS:
            - Mínimo de {min_words} palavras (ideal: {min_words + 200} palavras)
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
            
            CATEGORIA: {category or 'geral'}
            
            Certifique-se de que o artigo seja substancial, informativo e otimizado para SEO.
            """
            
            ai_content = generate_article(long_article_prompt)

            if ai_content:
                title = strip_tags(ai_content.get("title", topic.title()))[:200]
                content = f'<p class="dek">{strip_tags(ai_content.get("dek", ""))[:220]}</p>\n{ai_content.get("html", "<p></p>")}'
                
                # Verificar se o conteúdo da IA tem pelo menos min_words palavras
                clean_content = strip_tags(content)
                word_count = len(clean_content.split())
                
                if word_count >= min_words:
                    self.stdout.write(f"✅ IA gerou {word_count} palavras")
                    return content
                else:
                    self.stdout.write(f"⚠ IA gerou apenas {word_count} palavras, usando conteúdo SEO estendido")

        except Exception as e:
            self.stdout.write(f"⚠ IA falhou: {e}")

        # Conteúdo otimizado para SEO com mais palavras
        return self._generate_seo_content_extended(topic, category, min_words)

    def _generate_seo_content_extended(self, topic, category, min_words):
        """Gera conteúdo otimizado para SEO com mais palavras"""
        topic_lower = topic.lower()
        category_lower = category.lower() if category else self._detect_category(topic_lower)

        # Conteúdo base
        base_content = f"""<p class="dek">Análise completa e detalhada sobre {topic_lower}, oferecendo informações atualizadas e insights valiosos para profissionais e interessados no tema.</p>

<h2>{topic.title()}: Análise Completa e Detalhada</h2>

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
</ul>"""

        # Seções adicionais baseadas na categoria
        additional_sections = self._get_category_specific_sections(topic_lower, category_lower)
        
        # Conteúdo final
        final_content = f"""{base_content}

{additional_sections}

<h3>Conclusão</h3>

<p>Esta matéria sobre {topic_lower} foi desenvolvida com base em informações atualizadas e análises de especialistas da área. O RadarBR continua acompanhando os desdobramentos desta notícia e manterá os leitores informados sobre novos desenvolvimentos relacionados ao tema.</p>

<p>O cenário atual é promissor e indica que o Brasil está no caminho certo para se consolidar como uma referência em {topic_lower}. A continuidade das políticas públicas e o engajamento do setor privado serão fundamentais para manter o ritmo de crescimento observado.</p>

<p>Para mais informações sobre {topic_lower} e outros assuntos relevantes para o Brasil, acompanhe nossas atualizações diárias e mantenha-se sempre bem informado sobre os temas que mais importam para o país.</p>"""

        return final_content

    def _get_category_specific_sections(self, topic_lower, category_lower):
        """Gera seções específicas por categoria"""
        sections = {
            "tecnologia": f"""
<h3>Contexto Histórico e Evolução</h3>

<p>Para entender melhor a situação atual, é importante analisar o contexto histórico que levou a essa situação. O Brasil tem passado por transformações significativas nos últimos anos, com mudanças que impactaram diretamente a vida dos cidadãos brasileiros.</p>

<p>Esta questão tem relevância especial no contexto brasileiro, onde as particularidades locais influenciam diretamente os resultados observados. O Brasil, com sua diversidade regional e cultural, apresenta desafios e oportunidades únicos.</p>

<h3>Análise Detalhada e Técnica</h3>

<p>Os especialistas brasileiros destacam que {topic_lower} tem ganhado cada vez mais relevância no cenário nacional. As mudanças observadas nos últimos meses indicam uma tendência consistente que merece atenção especial dos profissionais da área.</p>

<p>Do ponto de vista técnico, esta questão apresenta características específicas que merecem atenção especial dos profissionais da área. A implementação de novas tecnologias e metodologias tem revolucionado a forma como abordamos este tema.</p>

<h3>Impacto na Sociedade Brasileira</h3>

<p>A população brasileira tem sentido diretamente os efeitos das transformações relacionadas a {topic_lower}. Desde as grandes metrópoles como São Paulo e Rio de Janeiro até as cidades do interior, é possível observar mudanças significativas que afetam o dia a dia das pessoas.</p>

<p>O impacto social é especialmente relevante nas comunidades mais vulneráveis, onde essas transformações podem representar uma oportunidade de inclusão e desenvolvimento. Isso demonstra o potencial transformador desta questão para toda a sociedade brasileira.</p>

<h3>Perspectivas para o Futuro</h3>

<p>As projeções para {topic_lower} indicam que esta tendência deve se manter nos próximos anos, com possíveis desenvolvimentos que podem trazer benefícios adicionais para o Brasil. Os analistas são cautelosamente otimistas quanto ao futuro, destacando que o país tem todas as condições necessárias para se consolidar como uma referência na área.</p>

<p>Os investimentos planejados para os próximos anos devem acelerar ainda mais essa tendência positiva, criando novas oportunidades e consolidando o Brasil como um player importante neste cenário.</p>
""",
            "economia": f"""
<h3>Contexto Econômico Nacional</h3>

<p>O cenário econômico brasileiro tem passado por transformações significativas que impactam diretamente o desenvolvimento de {topic_lower}. A estabilidade macroeconômica e as políticas públicas têm criado um ambiente propício para o crescimento desta área.</p>

<h3>Análise de Mercado</h3>

<p>O mercado brasileiro apresenta características únicas que influenciam diretamente como {topic_lower} se desenvolve. A análise de dados e tendências mostra um crescimento consistente e sustentável.</p>

<h3>Impacto na Economia Brasileira</h3>

<p>O impacto de {topic_lower} na economia brasileira tem sido significativo, contribuindo para o crescimento do PIB e a geração de empregos. Este setor tem se mostrado resiliente mesmo em períodos de instabilidade econômica.</p>

<h3>Investimentos e Financiamento</h3>

<p>Os investimentos em {topic_lower} têm crescido exponencialmente nos últimos anos, tanto do setor público quanto privado. Esta tendência indica confiança no potencial de crescimento desta área.</p>
""",
            "política": f"""
<h3>Contexto Político Nacional</h3>

<p>O cenário político brasileiro tem influenciado diretamente o desenvolvimento de {topic_lower}. As políticas públicas e as decisões governamentais têm criado um ambiente que favorece o crescimento desta área.</p>

<h3>Políticas Públicas</h3>

<p>As políticas públicas relacionadas a {topic_lower} têm evoluído significativamente, criando um marco regulatório que favorece o desenvolvimento sustentável e a inovação.</p>

<h3>Impacto na Democracia</h3>

<p>O desenvolvimento de {topic_lower} tem contribuído para o fortalecimento da democracia brasileira, promovendo transparência e participação cidadã.</p>

<h3>Desafios e Oportunidades</h3>

<p>Embora existam desafios significativos, as oportunidades para o desenvolvimento de {topic_lower} no Brasil são abundantes e promissoras.</p>
""",
            "esportes": f"""
<h3>História dos Esportes no Brasil</h3>

<p>O Brasil tem uma rica tradição esportiva que remonta às primeiras décadas do século XX. Desde então, o país tem se destacado em diversas modalidades, criando uma cultura esportiva única.</p>

<h3>Impacto Cultural</h3>

<p>O esporte no Brasil vai além da competição. Ele representa uma forma de expressão cultural, unindo comunidades e criando identidades regionais.</p>

<h3>Desenvolvimento e Infraestrutura</h3>

<p>Nos últimos anos, o Brasil tem investido significativamente na infraestrutura esportiva. Esses investimentos têm gerado resultados positivos, tanto para os atletas quanto para a população em geral.</p>

<h3>Perspectivas para o Futuro</h3>

<p>As perspectivas para {topic_lower} no Brasil são promissoras, com investimentos crescentes e políticas públicas que favorecem o desenvolvimento esportivo.</p>
""",
            "saúde": f"""
<h3>Sistema de Saúde Brasileiro</h3>

<p>O Sistema Único de Saúde (SUS) tem sido fundamental para o desenvolvimento de {topic_lower} no Brasil. A universalidade e integralidade do sistema criam oportunidades únicas de desenvolvimento.</p>

<h3>Inovação em Saúde</h3>

<p>A inovação em saúde tem sido uma prioridade no Brasil, com investimentos crescentes em pesquisa e desenvolvimento. Esta tendência tem gerado resultados positivos para a população brasileira.</p>

<h3>Desafios da Saúde Pública</h3>

<p>Embora existam desafios significativos no sistema de saúde brasileiro, as oportunidades para o desenvolvimento de {topic_lower} são abundantes e promissoras.</p>

<h3>Qualidade de Vida</h3>

<p>O desenvolvimento de {topic_lower} tem contribuído significativamente para a melhoria da qualidade de vida da população brasileira.</p>
""",
            "meio ambiente": f"""
<h3>Sustentabilidade Ambiental</h3>

<p>A sustentabilidade ambiental tem sido uma prioridade crescente no Brasil, com políticas públicas e iniciativas privadas que favorecem o desenvolvimento de {topic_lower}.</p>

<h3>Preservação da Biodiversidade</h3>

<p>O Brasil possui uma das maiores biodiversidades do mundo, o que cria oportunidades únicas para o desenvolvimento de {topic_lower} de forma sustentável.</p>

<h3>Energias Renováveis</h3>

<p>O desenvolvimento de energias renováveis tem sido uma prioridade no Brasil, criando oportunidades para o crescimento de {topic_lower}.</p>

<h3>Mudanças Climáticas</h3>

<p>As mudanças climáticas representam um desafio global, mas também uma oportunidade para o desenvolvimento de soluções inovadoras em {topic_lower}.</p>
"""
        }
        
        return sections.get(category_lower, f"""
<h3>Contexto Histórico e Evolução</h3>

<p>Para entender melhor a situação atual, é importante analisar o contexto histórico que levou a essa situação. O Brasil tem passado por transformações significativas nos últimos anos, com mudanças que impactaram diretamente a vida dos cidadãos brasileiros.</p>

<h3>Análise Detalhada</h3>

<p>Os especialistas brasileiros destacam que {topic_lower} tem ganhado cada vez mais relevância no cenário nacional. As mudanças observadas nos últimos meses indicam uma tendência consistente que merece atenção especial dos profissionais da área.</p>

<h3>Impacto na Sociedade Brasileira</h3>

<p>A população brasileira tem sentido diretamente os efeitos das transformações relacionadas a {topic_lower}. Desde as grandes metrópoles como São Paulo e Rio de Janeiro até as cidades do interior, é possível observar mudanças significativas que afetam o dia a dia das pessoas.</p>

<h3>Perspectivas para o Futuro</h3>

<p>As projeções para {topic_lower} indicam que esta tendência deve se manter nos próximos anos, com possíveis desenvolvimentos que podem trazer benefícios adicionais para o Brasil.</p>
""")

    def _expand_content(self, content, topic, category, min_words):
        """Expande conteúdo se necessário"""
        # Se já tem mais palavras que o mínimo, retornar como está
        word_count = len(strip_tags(content).split())
        if word_count >= min_words:
            return content
        
        # Adicionar seções adicionais
        additional_sections = self._generate_additional_sections(topic, category)
        
        # Inserir antes da conclusão
        if '<h3>Conclusão</h3>' in content:
            content = content.replace('<h3>Conclusão</h3>', additional_sections + '<h3>Conclusão</h3>')
        else:
            content += additional_sections
        
        return content

    def _generate_additional_sections(self, topic, category):
        """Gera seções adicionais para expandir conteúdo"""
        topic_lower = topic.lower()
        
        sections = f"""

<h3>Impacto Regional no Brasil</h3>

<p>O impacto de {topic_lower} varia significativamente entre as diferentes regiões do Brasil. No Nordeste, por exemplo, as características específicas da região influenciam diretamente como este tema se desenvolve, criando oportunidades únicas de crescimento e desenvolvimento.</p>

<p>Na região Sul, a tradição industrial e tecnológica oferece um ambiente propício para o desenvolvimento de soluções inovadoras relacionadas a {topic_lower}. Esta vantagem competitiva tem sido aproveitada por empresas e profissionais locais.</p>

<h3>Tendências Emergentes</h3>

<p>As tendências emergentes relacionadas a {topic_lower} indicam uma evolução constante e positiva. Novas tecnologias e metodologias estão sendo desenvolvidas, criando oportunidades para profissionais e empresas brasileiras.</p>

<p>Essas tendências são acompanhadas de perto por especialistas e pesquisadores, que identificam padrões e desenvolvem estratégias para aproveitar as oportunidades que surgem.</p>

<h3>Casos de Sucesso</h3>

<p>Existem diversos casos de sucesso relacionados a {topic_lower} no Brasil que servem como referência e inspiração. Esses casos demonstram o potencial do país e a capacidade dos profissionais brasileiros de desenvolver soluções inovadoras.</p>

<p>Esses exemplos de sucesso são fundamentais para motivar outros profissionais e empresas a investirem nesta área, criando um ciclo virtuoso de crescimento e desenvolvimento.</p>

<h3>Recomendações e Próximos Passos</h3>

<p>Com base na análise apresentada, é possível identificar algumas recomendações importantes para o desenvolvimento futuro desta área. Essas recomendações são fundamentadas em dados concretos e na experiência de especialistas.</p>

<p>O primeiro passo é continuar investindo em pesquisa e desenvolvimento, garantindo que o Brasil mantenha sua posição de liderança. Além disso, é importante focar na formação de profissionais qualificados.</p>
"""
        
        return sections

    def _get_category(self, topic, category, Categoria):
        """Obtém ou cria categoria"""
        if category:
            category_name = category.title()
        else:
            category_name = self._detect_category(topic.lower()).title()
        
        if category_name == "Geral":
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

                self.stdout.write("🖼️  Imagem adicionada com sucesso")

        except Exception as e:
            self.stdout.write(f"⚠ Erro ao adicionar imagem: {e}")

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
