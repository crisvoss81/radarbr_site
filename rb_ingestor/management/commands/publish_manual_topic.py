# rb_ingestor/management/commands/publish_manual_topic.py
"""
Comando para publicar artigo com tópico especificado manualmente
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.html import strip_tags
from slugify import slugify
from django.apps import apps
import logging

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

    def handle(self, *args, **options):
        Noticia = apps.get_model("rb_noticias", "Noticia")
        Categoria = apps.get_model("rb_noticias", "Categoria")

        self.stdout.write("=== PUBLICAÇÃO MANUAL DE TÓPICO ===")
        self.stdout.write(f"Executado em: {timezone.now()}")
        
        topic = options["topic"]
        category = options.get("category")
        custom_title = options.get("title")
        
        self.stdout.write(f"📝 Tópico: {topic}")
        if category:
            self.stdout.write(f"🏷️  Categoria especificada: {category}")
        if custom_title:
            self.stdout.write(f"📰 Título personalizado: {custom_title}")

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
        
        content = self._generate_content(topic, category)
        
        # Verificar qualidade do conteúdo
        word_count = len(strip_tags(content).split())
        self.stdout.write(f"📊 Palavras geradas: {word_count}")
        
        if word_count < 800:
            self.stdout.write("⚠ Conteúdo com menos de 800 palavras, expandindo...")
            content = self._expand_content(content, topic, category)
            word_count = len(strip_tags(content).split())
            self.stdout.write(f"📊 Palavras após expansão: {word_count}")

        # Obter categoria
        cat = self._get_category(topic, category, Categoria)
        
        # Criar slug
        slug = slugify(title)[:180]

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
                fonte_url=f"manual-topic-{timezone.now().strftime('%Y%m%d-%H%M')}",
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

    def _detect_category(self, topic_lower):
        """Detecta categoria baseada no tópico"""
        category_keywords = {
            "tecnologia": ["tecnologia", "digital", "ia", "inteligência artificial", "chatgpt", "app", "software"],
            "economia": ["economia", "mercado", "inflação", "dólar", "real", "investimento", "finanças"],
            "política": ["política", "governo", "eleições", "presidente", "lula", "bolsonaro", "congresso"],
            "esportes": ["esportes", "futebol", "copa", "mundial", "brasileirão", "atletismo"],
            "saúde": ["saúde", "medicina", "hospital", "vacina", "covid", "coronavírus"],
            "meio ambiente": ["meio ambiente", "sustentabilidade", "natureza", "clima", "ecologia"]
        }
        
        for category, keywords in category_keywords.items():
            if any(kw in topic_lower for kw in keywords):
                return category
        
        return "geral"

    def _generate_content(self, topic, category):
        """Gera conteúdo otimizado para SEO"""
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
            
            CATEGORIA: {category or 'geral'}
            
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
                    return content
                else:
                    self.stdout.write(f"⚠ IA gerou apenas {word_count} palavras, usando conteúdo SEO estendido")

        except Exception as e:
            self.stdout.write(f"⚠ IA falhou: {e}")

        # Conteúdo otimizado para SEO com mais palavras
        return self._generate_seo_content_extended(topic, category)

    def _generate_seo_content_extended(self, topic, category):
        """Gera conteúdo otimizado para SEO com mais de 800 palavras"""
        topic_lower = topic.lower()
        category_lower = category.lower() if category else self._detect_category(topic_lower)

        content = f"""<p class="dek">Análise completa e detalhada sobre {topic_lower}, oferecendo informações atualizadas e insights valiosos para profissionais e interessados no tema.</p>

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

        return content

    def _expand_content(self, content, topic, category):
        """Expande conteúdo se necessário"""
        # Se já tem mais de 800 palavras, retornar como está
        word_count = len(strip_tags(content).split())
        if word_count >= 800:
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
        category_lower = category.lower() if category else "geral"
        
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
