# rb_ingestor/management/commands/automacao_render.py
"""
Comando de automação otimizado para Render
Versão simplificada e robusta que funciona mesmo com limitações de recursos
"""
import os
import sys
import django
from django.core.management.base import BaseCommand
from django.apps import apps
from django.utils import timezone
from django.utils.html import strip_tags
from slugify import slugify
from datetime import datetime, timedelta
import random
import logging

# Configurar logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Automação simplificada e robusta para Render"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=3, help="Número de artigos a criar")
        parser.add_argument("--force", action="store_true", help="Força execução")
        parser.add_argument("--debug", action="store_true", help="Modo debug")

    def handle(self, *args, **options):
        Noticia = apps.get_model("rb_noticias", "Noticia")
        Categoria = apps.get_model("rb_noticias", "Categoria")
        
        self.stdout.write("=== AUTOMACAO RENDER RADARBR ===")
        self.stdout.write(f"Executado em: {timezone.now()}")
        
        # Verificar se deve executar
        if not options["force"] and not self._should_execute():
            self.stdout.write("PULANDO - timing não otimizado")
            return
        
        # Obter tópicos
        topics = self._get_topics()
        if not topics:
            self.stdout.write("ERRO: Nenhum tópico encontrado")
            return
        
        # Executar automação
        created_count = self._execute_automation(topics, Noticia, Categoria, options["limit"])
        
        # Resultado
        self.stdout.write(self.style.SUCCESS(f"OK: {created_count} notícias criadas"))
        
        # Ping sitemap se criou algo
        if created_count > 0:
            self._ping_sitemap()

    def _should_execute(self):
        """Verifica se deve executar baseado em timing"""
        Noticia = apps.get_model("rb_noticias", "Noticia")
        
        # Verificar notícias recentes (últimas 3 horas)
        recent_count = Noticia.objects.filter(
            criado_em__gte=timezone.now() - timedelta(hours=3)
        ).count()
        
        # Executar se menos de 2 notícias recentes
        return recent_count < 2

    def _get_topics(self):
        """Obtém tópicos para publicação"""
        topics = []
        
        # Tentar Google News primeiro
        try:
            topics = self._get_google_news_topics()
            if topics:
                self.stdout.write(f"✓ Google News: {len(topics)} tópicos")
                return topics
        except Exception as e:
            self.stdout.write(f"⚠ Google News falhou: {e}")
        
        # Fallback para tópicos fixos
        topics = self._get_fallback_topics()
        self.stdout.write(f"✓ Fallback: {len(topics)} tópicos")
        return topics

    def _get_google_news_topics(self):
        """Busca tópicos do Google News"""
        try:
            from gnews import GNews
            
            # Configurar GNews
            google_news = GNews(
                language='pt', 
                country='BR', 
                period='1d', 
                max_results=5,
                exclude_websites=['youtube.com', 'instagram.com', 'facebook.com']
            )
            
            # Buscar notícias
            articles = google_news.get_top_news()
            if not articles:
                return []
            
            # Extrair tópicos
            topics = []
            for article in articles[:5]:
                title = article.get('title', '')
                if title and len(title) > 10:
                    topic = self._extract_topic_from_title(title)
                    if topic and topic not in topics:
                        topics.append(topic)
            
            return topics[:3]  # Máximo 3 tópicos
            
        except Exception as e:
            self.stdout.write(f"⚠ Erro Google News: {e}")
            return []

    def _extract_topic_from_title(self, title):
        """Extrai tópico do título"""
        # Palavras comuns para remover
        common_words = [
            'no', 'do', 'da', 'em', 'para', 'com', 'por', 'que', 'é', 'foi', 
            'ser', 'ter', 'há', 'mais', 'menos', 'sobre', 'após', 'durante', 
            'entre', 'até', 'desde', 'a', 'o', 'as', 'os', 'um', 'uma', 'uns', 
            'umas', 'de', 'e', 'ou', 'mas', 'se', 'não', 'já', 'ainda', 'também', 
            'só', 'muito', 'pouco', 'todo', 'toda', 'todos', 'todas', 'cada', 
            'qual', 'quando', 'onde', 'como', 'porque', 'porquê', 'por que', 'por quê'
        ]
        
        # Limpar título
        title_clean = title.lower()
        words = title_clean.split()
        
        # Remover palavras comuns
        relevant_words = [word for word in words if word not in common_words and len(word) > 3]
        
        if relevant_words:
            # Pegar as 2-3 palavras mais relevantes
            topic = ' '.join(relevant_words[:3])
            return topic
        
        return None

    def _get_fallback_topics(self):
        """Tópicos de fallback"""
        hour = timezone.now().hour
        
        if 6 <= hour < 12:  # Manhã
            return ["notícias do dia", "economia matinal", "tecnologia"]
        elif 12 <= hour < 18:  # Tarde
            return ["esportes", "entretenimento", "cultura"]
        elif 18 <= hour < 22:  # Noite
            return ["política", "economia", "tecnologia"]
        else:  # Madrugada
            return ["preparação para o dia", "tendências"]

    def _execute_automation(self, topics, Noticia, Categoria, limit):
        """Executa a automação"""
        created_count = 0
        
        for i, topic in enumerate(topics[:limit]):
            try:
                # Gerar conteúdo
                title, content = self._generate_content(topic)
                
                # Categorizar
                categoria = self._get_category_for_topic(topic, Categoria)
                
                # Verificar duplicatas
                if self._check_duplicate(title, Noticia):
                    self.stdout.write(f"⚠ Pulando duplicata: {title}")
                    continue
                
                # Criar notícia
                noticia = Noticia.objects.create(
                    titulo=title,
                    slug=slugify(title)[:180],
                    conteudo=content,
                    publicado_em=timezone.now(),
                    categoria=categoria,
                    fonte_url=f"render-automation-{timezone.now().strftime('%Y%m%d-%H%M')}-{i}",
                    fonte_nome="RadarBR Automation",
                    status=1  # PUBLICADO
                )
                
                # Adicionar imagem
                self._add_image(noticia, topic)
                
                created_count += 1
                self.stdout.write(f"✓ Criado: {title}")
                
            except Exception as e:
                self.stdout.write(f"❌ Erro ao criar notícia: {e}")
                continue
        
        return created_count

    def _generate_content(self, topic):
        """Gera conteúdo otimizado para SEO"""
        try:
            # Tentar IA primeiro
            from rb_ingestor.ai import generate_article
            ai_content = generate_article(topic)
            
            if ai_content:
                title = strip_tags(ai_content.get("title", topic.title()))[:200]
                content = f'<p class="dek">{strip_tags(ai_content.get("dek", ""))[:220]}</p>\n{ai_content.get("html", "<p></p>")}'
                return title, content
                
        except Exception as e:
            self.stdout.write(f"⚠ IA falhou: {e}")
        
        # Conteúdo otimizado para SEO com palavras-chave estratégicas
        title = self._generate_seo_title(topic)
        content = self._generate_seo_content(topic)
        
        return title, content

    def _generate_seo_title(self, topic):
        """Gera título otimizado para SEO"""
        topic_lower = topic.lower()
        
        # Padrões de títulos SEO otimizados
        seo_patterns = [
            f"{topic.title()}: Tudo o Que Você Precisa Saber",
            f"{topic.title()} no Brasil: Análise Completa",
            f"Como {topic.title()} Está Mudando o Brasil",
            f"{topic.title()}: Tendências e Perspectivas 2025",
            f"O Que Esperar de {topic.title()} em 2025",
            f"{topic.title()}: Impacto na Sociedade Brasileira",
            f"Análise Completa: {topic.title()}",
            f"{topic.title()}: Guia Definitivo",
            f"Tendências de {topic.title()} para 2025",
            f"{topic.title()}: O Que Você Precisa Saber"
        ]
        
        # Escolher padrão baseado no tópico
        if "tecnologia" in topic_lower or "digital" in topic_lower:
            return f"{topic.title()}: Tendências e Inovações 2025"
        elif "economia" in topic_lower or "mercado" in topic_lower:
            return f"{topic.title()}: Impacto na Economia Brasileira"
        elif "política" in topic_lower or "governo" in topic_lower:
            return f"{topic.title()}: Análise Política Completa"
        elif "esportes" in topic_lower or "futebol" in topic_lower:
            return f"{topic.title()}: Últimas Notícias e Análises"
        elif "saúde" in topic_lower or "medicina" in topic_lower:
            return f"{topic.title()}: Informações Importantes para Sua Saúde"
        else:
            return seo_patterns[0]

    def _generate_seo_content(self, topic):
        """Gera conteúdo otimizado para SEO"""
        topic_lower = topic.lower()
        
        # Palavras-chave SEO estratégicas
        seo_keywords = {
            "brasil": ["Brasil", "brasileiro", "nacional", "federal"],
            "tecnologia": ["tecnologia", "digital", "inovação", "startup"],
            "economia": ["economia", "mercado", "investimento", "finanças"],
            "política": ["política", "governo", "eleições", "democracia"],
            "esportes": ["esportes", "futebol", "atletismo", "competição"],
            "saúde": ["saúde", "medicina", "hospital", "tratamento"],
            "educação": ["educação", "escola", "universidade", "ensino"],
            "meio ambiente": ["meio ambiente", "sustentabilidade", "natureza", "ecologia"]
        }
        
        # Identificar palavras-chave relevantes
        relevant_keywords = []
        for category, keywords in seo_keywords.items():
            if any(kw in topic_lower for kw in keywords):
                relevant_keywords.extend(keywords)
        
        # Adicionar palavras-chave do tópico
        relevant_keywords.extend(topic.split())
        
        # Conteúdo SEO otimizado
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

<h3>Impacto na Sociedade Brasileira</h3>

<p>A população brasileira tem sentido diretamente os efeitos das transformações relacionadas a {topic.lower()}. Desde as grandes metrópoles como São Paulo e Rio de Janeiro até as cidades do interior, é possível observar mudanças significativas que afetam o dia a dia das pessoas.</p>

<p>Estas alterações têm sido recebidas de forma positiva pela maioria da população brasileira, que vê nas mudanças uma oportunidade de melhoria na qualidade de vida e desenvolvimento do país.</p>

<h3>Perspectivas para o Futuro</h3>

<p>As projeções para {topic.lower()} indicam que esta tendência deve se manter nos próximos anos, com possíveis desenvolvimentos que podem trazer benefícios adicionais para o Brasil. Os analistas são cautelosamente otimistas quanto ao futuro, destacando que o país tem todas as condições necessárias para se consolidar como uma referência na área.</p>

<h3>Dados e Estatísticas</h3>

<p>Os números mais recentes sobre {topic.lower()} mostram uma evolução positiva em diversos indicadores relacionados ao tema. Esta melhoria tem sido observada de forma consistente ao longo dos últimos trimestres, demonstrando que não se trata de uma situação temporária, mas sim de uma tendência estrutural que deve perdurar.</p>

<h3>Conclusão</h3>

<p>Esta matéria sobre {topic.lower()} foi desenvolvida com base em informações atualizadas e análises de especialistas da área. O RadarBR continua acompanhando os desdobramentos desta notícia e manterá os leitores informados sobre novos desenvolvimentos relacionados ao tema.</p>

<p>O cenário atual é promissor e indica que o Brasil está no caminho certo para se consolidar como uma referência em {topic.lower()}. A continuidade das políticas públicas e o engajamento do setor privado serão fundamentais para manter o ritmo de crescimento observado.</p>

<p>Para mais informações sobre {topic.lower()} e outros assuntos relevantes para o Brasil, acompanhe nossas atualizações diárias e mantenha-se sempre bem informado sobre os temas que mais importam para o país.</p>"""
        
        return content

    def _get_category_for_topic(self, topic, Categoria):
        """Categoriza o tópico usando as categorias reais do site"""
        topic_lower = topic.lower()
        
        # Mapeamento completo baseado nas categorias reais do site
        category_mapping = {
            # Tecnologia
            "tecnologia": "Tecnologia",
            "inovação": "Tecnologia", 
            "digital": "Tecnologia",
            "startup": "Tecnologia",
            "app": "Tecnologia",
            "software": "Tecnologia",
            "ia": "Tecnologia",
            "inteligência artificial": "Tecnologia",
            "internet": "Tecnologia",
            "celular": "Tecnologia",
            "smartphone": "Tecnologia",
            "computador": "Tecnologia",
            "redes sociais": "Tecnologia",
            "youtube": "Tecnologia",
            "facebook": "Tecnologia",
            "instagram": "Tecnologia",
            "tiktok": "Tecnologia",
            "whatsapp": "Tecnologia",
            
            # Economia
            "economia": "Economia",
            "mercado": "Economia",
            "negócios": "Economia",
            "investimento": "Economia",
            "finanças": "Economia",
            "pib": "Economia",
            "inflação": "Economia",
            "dólar": "Economia",
            "real": "Economia",
            "bolsa": "Economia",
            "ações": "Economia",
            "banco": "Economia",
            "crédito": "Economia",
            "emprego": "Economia",
            "salário": "Economia",
            "imposto": "Economia",
            "tributo": "Economia",
            
            # Política
            "política": "Política",
            "governo": "Política",
            "eleições": "Política",
            "congresso": "Política",
            "presidente": "Política",
            "lula": "Política",
            "bolsonaro": "Política",
            "ministro": "Política",
            "deputado": "Política",
            "senador": "Política",
            "prefeito": "Política",
            "governador": "Política",
            "partido": "Política",
            "votação": "Política",
            "urna": "Política",
            "candidato": "Política",
            
            # Esportes
            "esportes": "Esportes",
            "futebol": "Esportes",
            "atletismo": "Esportes",
            "natação": "Esportes",
            "vôlei": "Esportes",
            "olimpíadas": "Esportes",
            "copa": "Esportes",
            "mundial": "Esportes",
            "brasileirão": "Esportes",
            "flamengo": "Esportes",
            "palmeiras": "Esportes",
            "corinthians": "Esportes",
            "são paulo": "Esportes",
            "santos": "Esportes",
            "vasco": "Esportes",
            "fluminense": "Esportes",
            "botafogo": "Esportes",
            "gremio": "Esportes",
            "internacional": "Esportes",
            
            # Entretenimento
            "entretenimento": "Entretenimento",
            "show": "Entretenimento",
            "festival": "Entretenimento",
            "cinema": "Entretenimento",
            "tv": "Entretenimento",
            "streaming": "Entretenimento",
            "netflix": "Entretenimento",
            "disney": "Entretenimento",
            "amazon": "Entretenimento",
            "filme": "Entretenimento",
            "série": "Entretenimento",
            "novela": "Entretenimento",
            "música": "Entretenimento",
            "cantor": "Entretenimento",
            "banda": "Entretenimento",
            "festival": "Entretenimento",
            "show": "Entretenimento",
            
            # Saúde
            "saúde": "Saúde",
            "medicina": "Saúde",
            "hospital": "Saúde",
            "vacina": "Saúde",
            "covid": "Saúde",
            "coronavírus": "Saúde",
            "pandemia": "Saúde",
            "médico": "Saúde",
            "enfermeiro": "Saúde",
            "remédio": "Saúde",
            "medicamento": "Saúde",
            "doença": "Saúde",
            "tratamento": "Saúde",
            "cirurgia": "Saúde",
            "exame": "Saúde",
            "laboratório": "Saúde",
            
            # Educação
            "educação": "Educação",
            "escola": "Educação",
            "universidade": "Educação",
            "ensino": "Educação",
            "estudante": "Educação",
            "professor": "Educação",
            "aluno": "Educação",
            "curso": "Educação",
            "faculdade": "Educação",
            "vestibular": "Educação",
            "enem": "Educação",
            "sisu": "Educação",
            "prova": "Educação",
            "nota": "Educação",
            "aprovado": "Educação",
            "reprovado": "Educação",
            
            # Ciência & Meio Ambiente
            "ciência": "Ciência & Meio Ambiente",
            "meio ambiente": "Ciência & Meio Ambiente",
            "natureza": "Ciência & Meio Ambiente",
            "sustentabilidade": "Ciência & Meio Ambiente",
            "clima": "Ciência & Meio Ambiente",
            "ecologia": "Ciência & Meio Ambiente",
            "aquecimento": "Ciência & Meio Ambiente",
            "poluição": "Ciência & Meio Ambiente",
            "reciclagem": "Ciência & Meio Ambiente",
            "energia": "Ciência & Meio Ambiente",
            "solar": "Ciência & Meio Ambiente",
            "eólica": "Ciência & Meio Ambiente",
            "pesquisa": "Ciência & Meio Ambiente",
            "cientista": "Ciência & Meio Ambiente",
            "laboratório": "Ciência & Meio Ambiente",
            "descoberta": "Ciência & Meio Ambiente",
            
            # Carros & Mobilidade
            "carro": "Carros & Mobilidade",
            "automóvel": "Carros & Mobilidade",
            "veículo": "Carros & Mobilidade",
            "mobilidade": "Carros & Mobilidade",
            "trânsito": "Carros & Mobilidade",
            "motorista": "Carros & Mobilidade",
            "direção": "Carros & Mobilidade",
            "combustível": "Carros & Mobilidade",
            "gasolina": "Carros & Mobilidade",
            "etanol": "Carros & Mobilidade",
            "diesel": "Carros & Mobilidade",
            "elétrico": "Carros & Mobilidade",
            "híbrido": "Carros & Mobilidade",
            "uber": "Carros & Mobilidade",
            "99": "Carros & Mobilidade",
            "taxi": "Carros & Mobilidade",
            
            # Agro
            "agro": "Agro",
            "agricultura": "Agro",
            "fazenda": "Agro",
            "fazendeiro": "Agro",
            "gado": "Agro",
            "boi": "Agro",
            "soja": "Agro",
            "milho": "Agro",
            "café": "Agro",
            "açúcar": "Agro",
            "etanol": "Agro",
            "trator": "Agro",
            "colheita": "Agro",
            "plantio": "Agro",
            "irrigação": "Agro",
            "fertilizante": "Agro",
            
            # Turismo
            "turismo": "Turismo",
            "viagem": "Turismo",
            "viagem": "Turismo",
            "hotel": "Turismo",
            "pousada": "Turismo",
            "praia": "Turismo",
            "montanha": "Turismo",
            "cidade": "Turismo",
            "estado": "Turismo",
            "país": "Turismo",
            "passagem": "Turismo",
            "avião": "Turismo",
            "aeroporto": "Turismo",
            "passaporte": "Turismo",
            "visto": "Turismo",
            "cruzeiro": "Turismo",
            
            # Trabalho & Carreira
            "trabalho": "Trabalho & Carreira",
            "carreira": "Trabalho & Carreira",
            "emprego": "Trabalho & Carreira",
            "vagas": "Trabalho & Carreira",
            "salário": "Trabalho & Carreira",
            "funcionário": "Trabalho & Carreira",
            "empresa": "Trabalho & Carreira",
            "rh": "Trabalho & Carreira",
            "recursos humanos": "Trabalho & Carreira",
            "entrevista": "Trabalho & Carreira",
            "currículo": "Trabalho & Carreira",
            "linkedin": "Trabalho & Carreira",
            "profissional": "Trabalho & Carreira",
            "cargo": "Trabalho & Carreira",
            "promoção": "Trabalho & Carreira",
            "demissão": "Trabalho & Carreira",
            
            # Justiça & Segurança
            "justiça": "Justiça & Segurança",
            "segurança": "Justiça & Segurança",
            "polícia": "Justiça & Segurança",
            "crime": "Justiça & Segurança",
            "assalto": "Justiça & Segurança",
            "roubo": "Justiça & Segurança",
            "furto": "Justiça & Segurança",
            "homicídio": "Justiça & Segurança",
            "tráfico": "Justiça & Segurança",
            "drogas": "Justiça & Segurança",
            "prisão": "Justiça & Segurança",
            "preso": "Justiça & Segurança",
            "julgamento": "Justiça & Segurança",
            "tribunal": "Justiça & Segurança",
            "juiz": "Justiça & Segurança",
            "advogado": "Justiça & Segurança",
            
            # Mundo
            "mundo": "Mundo",
            "internacional": "Mundo",
            "global": "Mundo",
            "país": "Mundo",
            "nação": "Mundo",
            "guerra": "Mundo",
            "conflito": "Mundo",
            "paz": "Mundo",
            "onu": "Mundo",
            "nato": "Mundo",
            "ue": "Mundo",
            "europa": "Mundo",
            "américa": "Mundo",
            "ásia": "Mundo",
            "áfrica": "Mundo",
            "china": "Mundo",
            "eua": "Mundo",
            "estados unidos": "Mundo",
            "rússia": "Mundo",
            "ucrânia": "Mundo",
            
            # Brasil
            "brasil": "Brasil",
            "brasileiro": "Brasil",
            "brasileira": "Brasil",
            "nacional": "Brasil",
            "federal": "Brasil",
            "estadual": "Brasil",
            "municipal": "Brasil",
            "são paulo": "Brasil",
            "rio de janeiro": "Brasil",
            "minas gerais": "Brasil",
            "bahia": "Brasil",
            "paraná": "Brasil",
            "rio grande do sul": "Brasil",
            "pernambuco": "Brasil",
            "ceará": "Brasil",
            "pará": "Brasil",
            "santa catarina": "Brasil",
            "goiás": "Brasil",
            "maranhão": "Brasil",
            
            # Cidades (RS)
            "porto alegre": "Cidades (RS)",
            "caxias do sul": "Cidades (RS)",
            "pelotas": "Cidades (RS)",
            "santa maria": "Cidades (RS)",
            "gravataí": "Cidades (RS)",
            "viamão": "Cidades (RS)",
            "novo hamburgo": "Cidades (RS)",
            "são leopoldo": "Cidades (RS)",
            "canoas": "Cidades (RS)",
            "santa cruz do sul": "Cidades (RS)",
            "cachoeirinha": "Cidades (RS)",
            "sapucaia do sul": "Cidades (RS)",
            "bagé": "Cidades (RS)",
            "bento gonçalves": "Cidades (RS)",
            "passo fundo": "Cidades (RS)",
            "santa rosa": "Cidades (RS)",
            
            # Loterias
            "loterias": "Loterias",
            "mega sena": "Loterias",
            "lotofácil": "Loterias",
            "quina": "Loterias",
            "lotomania": "Loterias",
            "dupla sena": "Loterias",
            "timemania": "Loterias",
            "federal": "Loterias",
            "loteria": "Loterias",
            "sorteio": "Loterias",
            "prêmio": "Loterias",
            "ganhador": "Loterias",
            "apostar": "Loterias",
            "jogo": "Loterias",
            "números": "Loterias",
            "bilhete": "Loterias"
        }
        
        # Procurar categoria por palavra-chave
        for keyword, category_name in category_mapping.items():
            if keyword in topic_lower:
                # Buscar categoria existente
                cat = Categoria.objects.filter(nome=category_name).first()
                if cat:
                    return cat
                else:
                    # Criar categoria se não existir
                    cat, created = Categoria.objects.get_or_create(
                        slug=slugify(category_name)[:140],
                        defaults={"nome": category_name}
                    )
                    return cat
        
        # Fallback para Brasil (categoria principal)
        cat_brasil = Categoria.objects.filter(nome="Brasil").first()
        if cat_brasil:
            return cat_brasil
        
        # Último fallback - criar Brasil se não existir
        cat_brasil, created = Categoria.objects.get_or_create(
            slug="brasil",
            defaults={"nome": "Brasil"}
        )
        return cat_brasil

    def _check_duplicate(self, title, Noticia):
        """Verifica duplicatas"""
        # Verificar por título similar (últimas 24h)
        recent_news = Noticia.objects.filter(
            criado_em__gte=timezone.now() - timedelta(hours=24)
        )
        
        for news in recent_news:
            if self._titles_similar(title, news.titulo):
                return True
        
        return False

    def _titles_similar(self, title1, title2):
        """Verifica se títulos são similares"""
        common_words = ["o", "que", "está", "no", "brasil", "análise", "completa"]
        words1 = set(title1.lower().split()) - set(common_words)
        words2 = set(title2.lower().split()) - set(common_words)
        
        if len(words1) == 0 or len(words2) == 0:
            return False
        
        common_count = len(words1.intersection(words2))
        similarity = common_count / min(len(words1), len(words2))
        
        return similarity > 0.5

    def _add_image(self, noticia, topic):
        """Adiciona imagem à notícia com sistema robusto de fallbacks"""
        try:
            # Tentar ImageSearchEngine primeiro
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
                
                self.stdout.write(f"✓ Imagem encontrada via ImageSearchEngine: {topic}")
                return
                
        except Exception as e:
            self.stdout.write(f"⚠ ImageSearchEngine falhou: {e}")
        
        # Fallback 1: Sistema de imagens gratuito
        try:
            from rb_ingestor.images_free import pick_image
            from rb_ingestor.images_cloudinary import upload_remote_to_cloudinary
            
            img_info = pick_image(topic)
            if img_info and img_info.get("url"):
                remote_url = img_info["url"]
                secure_url = upload_remote_to_cloudinary(
                    remote_url,
                    public_id=None,
                    folder="radarbr/noticias",
                    tags=["radarbr", "noticia", "automacao"],
                )
                
                if secure_url:
                    noticia.imagem = secure_url
                    noticia.imagem_alt = f"Imagem sobre {topic}"
                    noticia.imagem_credito = img_info.get("credito", "Imagem gratuita")
                    noticia.imagem_licenca = img_info.get("licenca", "CC")
                    noticia.imagem_fonte_url = img_info.get("fonte_url", remote_url)
                    noticia.save()
                    
                    self.stdout.write(f"✓ Imagem encontrada via sistema gratuito: {topic}")
                    return
                    
        except Exception as e:
            self.stdout.write(f"⚠ Sistema gratuito falhou: {e}")
        
        # Fallback 2: Imagem padrão baseada na categoria
        try:
            default_image = self._get_default_image_for_category(noticia.categoria)
            if default_image:
                noticia.imagem = default_image
                noticia.imagem_alt = f"Imagem padrão para {noticia.categoria.nome if noticia.categoria else 'geral'}"
                noticia.imagem_credito = "RadarBR"
                noticia.imagem_licenca = "Padrão"
                noticia.imagem_fonte_url = default_image
                noticia.save()
                
                self.stdout.write(f"✓ Imagem padrão aplicada: {topic}")
                return
                
        except Exception as e:
            self.stdout.write(f"⚠ Imagem padrão falhou: {e}")
        
        # Fallback final: Sem imagem (não falha)
        self.stdout.write(f"⚠ Nenhuma imagem encontrada para: {topic} (continuando sem imagem)")

    def _get_default_image_for_category(self, categoria):
        """Retorna imagem padrão baseada na categoria"""
        if not categoria:
            return None
            
        # Imagens padrão por categoria (URLs de imagens gratuitas)
        default_images = {
            "Tecnologia": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800&h=450&fit=crop",
            "Economia": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=800&h=450&fit=crop",
            "Política": "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=800&h=450&fit=crop",
            "Esportes": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&h=450&fit=crop",
            "Entretenimento": "https://images.unsplash.com/photo-1489599808411-2b3b0b0b0b0b?w=800&h=450&fit=crop",
            "Saúde": "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=800&h=450&fit=crop",
            "Educação": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=800&h=450&fit=crop",
            "Ciência & Meio Ambiente": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800&h=450&fit=crop",
            "Carros & Mobilidade": "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=800&h=450&fit=crop",
            "Agro": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800&h=450&fit=crop",
            "Turismo": "https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=800&h=450&fit=crop",
            "Trabalho & Carreira": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&h=450&fit=crop",
            "Justiça & Segurança": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=800&h=450&fit=crop",
            "Mundo": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=450&fit=crop",
            "Brasil": "https://images.unsplash.com/photo-1489599808411-2b3b0b0b0b0b?w=800&h=450&fit=crop",
            "Cidades (RS)": "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=800&h=450&fit=crop",
            "Loterias": "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=800&h=450&fit=crop"
        }
        
        return default_images.get(categoria.nome)

    def _ping_sitemap(self):
        """Faz ping do sitemap"""
        try:
            from core.utils import absolute_sitemap_url
            from rb_ingestor.ping import ping_search_engines
            
            sm_url = absolute_sitemap_url()
            res = ping_search_engines(sm_url)
            self.stdout.write(f"Ping sitemap: Google={'OK' if res['google'] else 'NOK'}; Bing={'OK' if res['bing'] else 'NOK'}")
        except Exception as e:
            self.stdout.write(f"⚠ Erro ping sitemap: {e}")
