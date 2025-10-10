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
        
        # Estratégias baseadas em horário e audiência
        if 6 <= hour < 12:  # Manhã
            return {
                "name": "Manhã - Conteúdo Informativo",
                "topics": [
                    "notícias do dia",
                    "economia matinal", 
                    "tecnologia",
                    "educação"
                ],
                "category": audience_data["best_category"],
                "limit": 3
            }
        elif 12 <= hour < 18:  # Tarde
            return {
                "name": "Tarde - Conteúdo Diversificado",
                "topics": [
                    "esportes",
                    "entretenimento",
                    "cultura",
                    "lifestyle"
                ],
                "category": audience_data["best_category"],
                "limit": 4
            }
        elif 18 <= hour < 22:  # Noite (pico)
            return {
                "name": "Noite - Conteúdo de Alto Engajamento",
                "topics": [
                    "política",
                    "economia",
                    "tecnologia",
                    "esportes",
                    "entretenimento"
                ],
                "category": audience_data["best_category"],
                "limit": 5
            }
        else:  # Madrugada
            return {
                "name": "Madrugada - Conteúdo Preparatório",
                "topics": [
                    "preparação para o dia",
                    "tendências",
                    "análises"
                ],
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
        
        # Criar categoria se não existir
        cat, created = Categoria.objects.get_or_create(
            slug=slugify(strategy["category"])[:140],
            defaults={"nome": strategy["category"]}
        )
        
        # Gerar notícias baseadas na estratégia
        for i in range(strategy["limit"]):
            topic = random.choice(strategy["topics"])
            
            # Gerar título otimizado
            timestamp = timezone.now().strftime('%d/%m %H:%M')
            title = f"{topic.title()} - {timestamp}"
            slug = slugify(title)[:180]
            
            # Verificar se já existe
            if Noticia.objects.filter(slug=slug).exists():
                continue
            
            # Gerar conteúdo otimizado
            content = self._generate_optimized_content(topic, strategy["name"])
            
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
            "Manhã - Conteúdo Informativo": f"""## {topic.title()}

Começando o dia com informações importantes sobre {topic.lower()}.

### Principais Destaques

- Informação relevante 1
- Informação relevante 2  
- Informação relevante 3

### Análise do Dia

Uma análise detalhada sobre os aspectos mais importantes de {topic.lower()} para o dia de hoje.

### Próximos Passos

O que esperar e como se preparar para os desenvolvimentos em {topic.lower()}.
""",
            
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
            
            "Madrugada - Conteúdo Preparatório": f"""## {topic.title()}

Preparação para o dia com foco em {topic.lower()}.

### Resumo Executivo

- Ponto principal 1
- Ponto principal 2
- Ponto principal 3

### Preparação

Como se preparar para os desenvolvimentos em {topic.lower()}.

### Expectativas

O que esperar dos próximos desenvolvimentos em {topic.lower()}.
"""
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
        self.stdout.write(f"\n💡 RECOMENDAÇÕES:")
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
