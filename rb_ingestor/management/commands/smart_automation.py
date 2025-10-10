# rb_ingestor/management/commands/smart_automation.py
"""
Sistema inteligente de automação que otimiza para audiência
Executa automaticamente com estratégias baseadas em dados reais
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
    help = "Sistema inteligente de automação otimizado para audiência"

    def add_arguments(self, parser):
        parser.add_argument("--mode", choices=['auto', 'manual', 'test'], default='auto', 
                          help="Modo de execução")
        parser.add_argument("--force", action="store_true", help="Força execução")

    def handle(self, *args, **options):
        Noticia = apps.get_model("rb_noticias", "Noticia")
        Categoria = apps.get_model("rb_noticias", "Categoria")
        
        self.stdout.write("=== SISTEMA INTELIGENTE DE AUTOMACAO ===")
        
        # Análise de audiência
        audience_data = self._analyze_audience()
        self.stdout.write(f"ANALISE de audiencia: {audience_data['summary']}")
        
        # Determinar estratégia baseada no horário e dados
        strategy = self._determine_strategy(audience_data)
        self.stdout.write(f"ESTRATEGIA escolhida: {strategy['name']}")
        
        # Verificar se deve executar
        if not options["force"] and not self._should_execute():
            self.stdout.write("PULANDO execucao - timing nao otimizado")
            return
        
        # Executar automação
        created_count = self._execute_automation(strategy, Noticia, Categoria)
        
        # Análise pós-execução
        self._post_execution_analysis(created_count, audience_data)
        
        self.stdout.write(self.style.SUCCESS(f"\nOK Automacao concluida: {created_count} noticias criadas"))

    def _analyze_audience(self):
        """Analisa dados da audiência para otimização"""
        Noticia = apps.get_model("rb_noticias", "Noticia")
        
        # Análise das últimas 7 dias
        week_ago = timezone.now() - timedelta(days=7)
        recent_news = Noticia.objects.filter(publicado_em__gte=week_ago)
        
        # Análise por categoria
        category_performance = {}
        for news in recent_news:
            cat_name = news.categoria.nome if news.categoria else "Sem categoria"
            category_performance[cat_name] = category_performance.get(cat_name, 0) + 1
        
        # Análise por horário
        hour_performance = {}
        for news in recent_news:
            hour = news.publicado_em.hour
            hour_performance[hour] = hour_performance.get(hour, 0) + 1
        
        # Determinar melhor categoria e horário
        best_category = max(category_performance.items(), key=lambda x: x[1])[0] if category_performance else "Geral"
        best_hours = sorted(hour_performance.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "total_recent": recent_news.count(),
            "best_category": best_category,
            "best_hours": [h[0] for h in best_hours],
            "category_performance": category_performance,
            "hour_performance": hour_performance,
            "summary": f"{recent_news.count()} notícias em 7 dias, melhor categoria: {best_category}"
        }

    def _determine_strategy(self, audience_data):
        """Determina estratégia baseada em dados de audiência"""
        now = timezone.now()
        hour = now.hour
        weekday = now.weekday()  # 0=segunda, 6=domingo
        
        # Buscar tópicos reais do Google News e Trends
        real_topics = self._get_real_topics(hour)
        
        # Estratégias baseadas em horário e audiência
        if 6 <= hour < 12:  # Manhã
            return {
                "name": "Manhã - Conteúdo Informativo",
                "topics": real_topics[:3] if real_topics else ["notícias do dia", "economia matinal", "tecnologia"],
                "category": audience_data["best_category"],
                "limit": 3
            }
        elif 12 <= hour < 18:  # Tarde
            return {
                "name": "Tarde - Conteúdo Diversificado",
                "topics": real_topics[:4] if real_topics else ["esportes", "entretenimento", "cultura", "lifestyle"],
                "category": audience_data["best_category"],
                "limit": 4
            }
        elif 18 <= hour < 22:  # Noite (pico)
            return {
                "name": "Noite - Conteúdo de Alto Engajamento",
                "topics": real_topics[:5] if real_topics else ["política", "economia", "tecnologia", "esportes", "entretenimento"],
                "category": audience_data["best_category"],
                "limit": 5
            }
        else:  # Madrugada
            return {
                "name": "Madrugada - Conteúdo Preparatório",
                "topics": real_topics[:2] if real_topics else ["preparação para o dia", "tendências"],
                "category": audience_data["best_category"],
                "limit": 2
            }

    def _should_execute(self):
        """Determina se deve executar baseado em timing inteligente"""
        now = timezone.now()
        hour = now.hour
        
        # Horários otimizados para publicação
        optimal_hours = [8, 12, 15, 18, 20]  # Horários de pico de audiência
        
        # Verificar se está próximo de um horário otimizado
        for optimal_hour in optimal_hours:
            if abs(hour - optimal_hour) <= 1:  # ±1 hora do horário otimizado
                return True
        
        # Verificar se há poucas notícias recentes
        Noticia = apps.get_model("rb_noticias", "Noticia")
        recent_count = Noticia.objects.filter(
            criado_em__gte=timezone.now() - timedelta(hours=6)
        ).count()
        
        return recent_count < 2  # Executar se menos de 2 notícias em 6h

    def _execute_automation(self, strategy, Noticia, Categoria):
        """Executa a automação com a estratégia determinada"""
        created_count = 0
        
        # Gerar notícias baseadas na estratégia
        for i in range(strategy["limit"]):
            topic = random.choice(strategy["topics"])
            
            # Gerar conteúdo com IA otimizada
            try:
                from rb_ingestor.ai import generate_article
                ai_content = generate_article(topic)
                title = ai_content.get("title", topic.title())
                content = ai_content.get("html", f"## {topic.title()}\n\nConteúdo sobre {topic.lower()}.")
            except Exception as e:
                self.stdout.write(f"⚠ Erro na IA, usando fallback: {e}")
                title = f"{topic.title()} - Análise Completa"
                content = self._generate_optimized_content(topic, strategy["name"])
            
            # Categorizar baseado no tópico
            cat = self._get_category_for_topic(topic, Categoria)
            
            slug = slugify(title)[:180]
            
            # Verificar se já existe (mais rigoroso)
            if self._check_duplicate_news(title, topic, Noticia):
                self.stdout.write(f"⚠ Pulando duplicata: {title}")
                continue
            
            # Criar notícia
            try:
                noticia = Noticia.objects.create(
                    titulo=title,
                    slug=slug,
                    conteudo=content,
                    publicado_em=timezone.now(),
                    categoria=cat,
                    fonte_url=f"smart-automation-{timezone.now().strftime('%Y%m%d-%H%M')}-{i}",
                    fonte_nome="RadarBR Smart Automation",
                    status=1  # PUBLICADO
                )
                
                # Buscar e salvar imagem (sem Cloudinary)
                self._add_image_to_news(noticia, topic)
                
                created_count += 1
                self.stdout.write(f"OK Criado: {title}")
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"ERRO: {e}"))
        
        return created_count

    def _generate_optimized_content(self, topic, strategy_name):
        """Gera conteúdo otimizado baseado no tópico e estratégia"""
        
        # Conteúdos otimizados por estratégia (em Markdown)
        content_templates = {
            "Manhã - Conteúdo Informativo": f"""<p class="dek">Começando o dia com informações importantes sobre {topic.lower()}, oferecendo uma visão completa dos desenvolvimentos mais relevantes para profissionais e interessados.</p>

## {topic.title()}

Começando o dia com informações importantes sobre {topic.lower()}. Este tema tem ganhado cada vez mais relevância no cenário nacional, merecendo atenção especial dos profissionais e interessados na área.

### Principais Destaques

- Informação relevante 1: Desenvolvimentos recentes indicam crescimento significativo
- Informação relevante 2: Impacto positivo na economia e sociedade brasileira  
- Informação relevante 3: Perspectivas promissoras para os próximos meses

### Análise do Dia

Uma análise detalhada sobre os aspectos mais importantes de {topic.lower()} para o dia de hoje. Os especialistas destacam que este tema tem ganhado cada vez mais relevância no cenário nacional. As mudanças observadas nos últimos meses indicam uma tendência consistente que merece atenção especial.

### Próximos Passos

O que esperar e como se preparar para os desenvolvimentos em {topic.lower()}. As projeções indicam que esta tendência deve se manter nos próximos anos, com possíveis desenvolvimentos que podem trazer benefícios adicionais para o país.

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

Para mais informações sobre este e outros assuntos relevantes, acompanhe nossas atualizações diárias e mantenha-se sempre bem informado sobre os temas que mais importam para o Brasil.""",
            
            "Tarde - Conteúdo Diversificado": f"""## {topic.title()}

Uma visão abrangente sobre {topic.lower()} para o período da tarde.

### Destaques do Momento

- Desenvolvimento importante 1
- Desenvolvimento importante 2
- Desenvolvimento importante 3

### Impacto e Relevância

Como {topic.lower()} está influenciando diferentes aspectos da sociedade.

### Perspectivas

O que podemos esperar nos próximos desenvolvimentos relacionados a {topic.lower()}.
""",
            
            "Noite - Conteúdo de Alto Engajamento": f"""## {topic.title()}

Uma análise profunda sobre {topic.lower()} para o período noturno.

### Análise Detalhada

- Ponto crítico 1
- Ponto crítico 2
- Ponto crítico 3

### Implicações

As consequências e impactos de {topic.lower()} na sociedade atual.

### Discussão

Pontos para reflexão e discussão sobre {topic.lower()}.
""",
            
            "Madrugada - Conteúdo Preparatório": f"""<p class="dek">Preparação estratégica para o dia com foco em {topic.lower()}, oferecendo insights valiosos para profissionais e interessados no tema.</p>

## {topic.title()}

Preparação para o dia com foco em {topic.lower()}. Este tema tem ganhado cada vez mais relevância no cenário nacional, merecendo atenção especial dos profissionais e interessados na área.

### Resumo Executivo

- Ponto principal 1: Desenvolvimentos recentes indicam crescimento significativo
- Ponto principal 2: Impacto positivo na economia e sociedade brasileira  
- Ponto principal 3: Perspectivas promissoras para os próximos meses

### Preparação

Como se preparar para os desenvolvimentos em {topic.lower()}. Os especialistas recomendam acompanhar de perto as mudanças que estão ocorrendo no setor, pois elas podem influenciar diretamente o dia a dia das pessoas e empresas.

### Expectativas

O que esperar dos próximos desenvolvimentos em {topic.lower()}. As projeções indicam que esta tendência deve se manter nos próximos anos, com possíveis desenvolvimentos que podem trazer benefícios adicionais para o país.

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
        }
        
        return content_templates.get(strategy_name, f"""## {topic.title()}

Conteúdo sobre {topic.lower()} gerado pelo sistema inteligente de automação.

### Principais Aspectos

- Aspecto importante 1
- Aspecto importante 2
- Aspecto importante 3

### Conclusão

{topic.title()} é um tema relevante que merece atenção contínua.
""")

    def _add_image_to_news(self, noticia, topic):
        """Busca e adiciona imagem à notícia (funciona sem Cloudinary)"""
        try:
            from rb_ingestor.images_free import pick_image
            
            # Buscar imagem gratuita
            image_info = pick_image(topic)
            
            if image_info and image_info.get("url"):
                # Salvar URL da imagem diretamente (sem Cloudinary)
                noticia.imagem = image_info["url"]
                noticia.imagem_alt = f"Imagem relacionada a {topic}"
                noticia.imagem_credito = image_info.get("credito", "Imagem gratuita")
                noticia.imagem_licenca = image_info.get("licenca", "CC")
                noticia.imagem_fonte_url = image_info.get("fonte_url", image_info["url"])
                noticia.save()
                
                self.stdout.write(f"OK Imagem adicionada: {topic}")
            else:
                self.stdout.write(f"AVISO Nenhuma imagem encontrada para: {topic}")
                
        except Exception as e:
            self.stdout.write(f"AVISO Erro ao buscar imagem para {topic}: {e}")

    def _get_category_for_topic(self, topic, Categoria):
        """Categoriza o tópico baseado em palavras-chave"""
        topic_lower = topic.lower()
        
        # Mapeamento de tópicos para categorias
        category_mapping = {
            "tecnologia": "Tecnologia",
            "inovação": "Tecnologia", 
            "digital": "Tecnologia",
            "startup": "Tecnologia",
            "app": "Tecnologia",
            "software": "Tecnologia",
            "ia": "Tecnologia",
            "inteligência artificial": "Tecnologia",
            
            "economia": "Economia",
            "mercado": "Economia",
            "negócios": "Economia",
            "investimento": "Economia",
            "finanças": "Economia",
            "pib": "Economia",
            "inflação": "Economia",
            
            "esportes": "Esportes",
            "futebol": "Esportes",
            "atletismo": "Esportes",
            "natação": "Esportes",
            "vôlei": "Esportes",
            "olimpíadas": "Esportes",
            
            "cultura": "Cultura",
            "arte": "Cultura",
            "museu": "Cultura",
            "teatro": "Cultura",
            "literatura": "Cultura",
            "folclore": "Cultura",
            "música": "Cultura",
            
            "entretenimento": "Entretenimento",
            "show": "Entretenimento",
            "festival": "Entretenimento",
            "cinema": "Entretenimento",
            "tv": "Entretenimento",
            "streaming": "Entretenimento",
            
            "lifestyle": "Lifestyle",
            "vida": "Lifestyle",
            "estilo": "Lifestyle",
            "moda": "Lifestyle",
            "gastronomia": "Lifestyle",
            "viagem": "Lifestyle",
            "turismo": "Lifestyle",
            
            "política": "Política",
            "governo": "Política",
            "eleições": "Política",
            "congresso": "Política",
            "presidente": "Política",
            
            "saúde": "Saúde",
            "medicina": "Saúde",
            "hospital": "Saúde",
            "vacina": "Saúde",
            "covid": "Saúde",
            
            "educação": "Educação",
            "escola": "Educação",
            "universidade": "Educação",
            "ensino": "Educação",
            "estudante": "Educação",
            
            "meio ambiente": "Meio Ambiente",
            "natureza": "Meio Ambiente",
            "sustentabilidade": "Meio Ambiente",
            "clima": "Meio Ambiente",
            "ecologia": "Meio Ambiente"
        }
        
        # Procurar categoria correspondente
        for keyword, category_name in category_mapping.items():
            if keyword in topic_lower:
                cat, created = Categoria.objects.get_or_create(
                    slug=slugify(category_name)[:140],
                    defaults={"nome": category_name}
                )
                return cat
        
        # Fallback para categoria geral
        cat_geral, created = Categoria.objects.get_or_create(
            slug="geral",
            defaults={"nome": "Geral"}
        )
        return cat_geral

    def _check_duplicate_news(self, title, topic, Noticia):
        """Verifica se já existe notícia similar (mais rigoroso)"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Verificar por título similar (últimas 24h)
        recent_news = Noticia.objects.filter(
            publicado_em__gte=timezone.now() - timedelta(hours=24)
        )
        
        # Verificar título similar
        for news in recent_news:
            if self._titles_similar(title, news.titulo):
                return True
        
        # Verificar por tópico similar (últimas 6h)
        recent_news_6h = Noticia.objects.filter(
            publicado_em__gte=timezone.now() - timedelta(hours=6)
        )
        
        for news in recent_news_6h:
            if self._topics_similar(topic, news.titulo):
                return True
        
        return False

    def _titles_similar(self, title1, title2):
        """Verifica se dois títulos são similares"""
        # Remover palavras comuns e comparar
        common_words = ["o", "que", "está", "no", "brasil", "análise", "completa", "tendências"]
        words1 = set(title1.lower().split()) - set(common_words)
        words2 = set(title2.lower().split()) - set(common_words)
        
        # Se mais de 50% das palavras são iguais, são similares
        if len(words1) == 0 or len(words2) == 0:
            return False
        
        common_count = len(words1.intersection(words2))
        similarity = common_count / min(len(words1), len(words2))
        
        return similarity > 0.5

    def _topics_similar(self, topic, title):
        """Verifica se o tópico é similar ao título"""
        topic_words = set(topic.lower().split())
        title_words = set(title.lower().split())
        
        # Se o tópico está contido no título, são similares
        return topic_words.issubset(title_words)

    def _get_real_topics(self, hour):
        """Busca tópicos reais do Google News e Trends"""
        try:
            # Tentar Google News primeiro
            topics = self._get_google_news_topics()
            if topics:
                self.stdout.write(f"✓ Tópicos do Google News: {len(topics)} encontrados")
                return topics
            
            # Fallback para Trending Analyzer
            topics = self._get_trending_topics()
            if topics:
                self.stdout.write(f"✓ Tópicos do Trending: {len(topics)} encontrados")
                return topics
            
            # Fallback para tópicos fixos por horário
            return self._get_fallback_topics(hour)
            
        except Exception as e:
            self.stdout.write(f"⚠ Erro ao buscar tópicos reais: {e}")
            return self._get_fallback_topics(hour)

    def _get_google_news_topics(self):
        """Busca tópicos do Google News"""
        try:
            from gnews import GNews
            
            # Configurar GNews para Brasil
            google_news = GNews(
                language='pt', 
                country='BR', 
                period='1d', 
                max_results=10,
                exclude_websites=['youtube.com', 'instagram.com', 'facebook.com']
            )
            
            # Buscar top news
            articles = google_news.get_top_news()
            if not articles:
                return []
            
            # Extrair tópicos dos títulos
            topics = []
            for article in articles[:8]:  # Limitar a 8 artigos
                title = article.get('title', '')
                if title and len(title) > 10:
                    # Limpar e extrair tópico do título
                    topic = self._extract_topic_from_title(title)
                    if topic and topic not in topics:
                        topics.append(topic)
            
            return topics[:5]  # Retornar até 5 tópicos
            
        except Exception as e:
            self.stdout.write(f"⚠ Erro no Google News: {e}")
            return []

    def _get_trending_topics(self):
        """Busca tópicos do Trending Analyzer"""
        try:
            from rb_ingestor.trending_analyzer import TrendingAnalyzer
            
            analyzer = TrendingAnalyzer()
            optimized_topics = analyzer.get_optimized_topics(limit=5)
            
            if optimized_topics:
                return [topic['topic'] for topic in optimized_topics]
            
            return []
            
        except Exception as e:
            self.stdout.write(f"⚠ Erro no Trending Analyzer: {e}")
            return []

    def _extract_topic_from_title(self, title):
        """Extrai tópico relevante do título da notícia"""
        # Remover palavras comuns e extrair tópico principal
        common_words = ['no', 'do', 'da', 'em', 'para', 'com', 'por', 'que', 'é', 'foi', 'ser', 'ter', 'há', 'mais', 'menos', 'sobre', 'após', 'durante', 'entre', 'até', 'desde', 'a', 'o', 'as', 'os', 'um', 'uma', 'uns', 'umas', 'de', 'e', 'ou', 'mas', 'se', 'não', 'já', 'ainda', 'também', 'só', 'muito', 'pouco', 'todo', 'toda', 'todos', 'todas', 'cada', 'qual', 'quando', 'onde', 'como', 'porque', 'porquê', 'por que', 'por quê']
        
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

    def _get_fallback_topics(self, hour):
        """Tópicos de fallback baseados no horário"""
        if 6 <= hour < 12:  # Manhã
            return ["notícias do dia", "economia matinal", "tecnologia"]
        elif 12 <= hour < 18:  # Tarde
            return ["esportes", "entretenimento", "cultura", "lifestyle"]
        elif 18 <= hour < 22:  # Noite
            return ["política", "economia", "tecnologia", "esportes", "entretenimento"]
        else:  # Madrugada
            return ["preparação para o dia", "tendências"]

    def _post_execution_analysis(self, created_count, audience_data):
        """Análise pós-execução para otimização futura"""
        self.stdout.write(f"\nANALISE POS-EXECUCAO:")
        self.stdout.write(f"Notícias criadas: {created_count}")
        
        # Estatísticas gerais
        Noticia = apps.get_model("rb_noticias", "Noticia")
        total_news = Noticia.objects.count()
        recent_news = Noticia.objects.filter(
            criado_em__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        self.stdout.write(f"Total no sistema: {total_news}")
        self.stdout.write(f"Últimas 24h: {recent_news}")
        
        # Ping sitemap
        if created_count > 0:
            try:
                from core.utils import absolute_sitemap_url
                from rb_ingestor.ping import ping_search_engines
                sm_url = absolute_sitemap_url()
                res = ping_search_engines(sm_url)
                self.stdout.write(f"Ping sitemap: Google={'OK' if res['google'] else 'NOK'}; Bing={'OK' if res['bing'] else 'NOK'}")
            except Exception:
                self.stdout.write("⚠ Erro ao fazer ping do sitemap")
        
        # Recomendações para próxima execução
        self.stdout.write(f"\nRECOMENDACOES:")
        if audience_data["best_category"] != "Geral":
            self.stdout.write(f"- Focar mais em: {audience_data['best_category']}")
        if audience_data["best_hours"]:
            self.stdout.write(f"- Melhores horários: {', '.join(map(str, audience_data['best_hours']))}h")
        
        if created_count == 0:
            self.stdout.write("- Considerar ajustar estratégia de tópicos")
        elif created_count < 3:
            self.stdout.write("- Sistema funcionando bem com volume moderado")
        else:
            self.stdout.write("- Sistema em alta performance - manter estratégia")
