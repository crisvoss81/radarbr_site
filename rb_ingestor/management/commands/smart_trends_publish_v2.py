# rb_ingestor/management/commands/smart_trends_publish_v2.py
"""
Comando inteligente para publicação de notícias baseado em análise de audiência
USANDO A MESMA LÓGICA DO PUBLISH_TOPIC
"""
import traceback
from django.core.management.base import BaseCommand
from django.apps import apps
from django.utils import timezone
from rb_ingestor.enhanced_trending_sources import EnhancedTrendingSources
from rb_ingestor.audience_analyzer import AudienceAnalyzer

class Command(BaseCommand):
    help = "Publica artigos baseado em temas em ascensão usando a mesma lógica do publish_topic"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=3, help="Número de artigos a serem criados.")
        parser.add_argument("--debug", action="store_true", help="Mostra mais informações sobre o processo.")
        parser.add_argument("--force", action="store_true", help="Força a publicação mesmo que um tópico similar já exista.")
        parser.add_argument("--strategy", choices=["trending", "audience", "mixed"], default="mixed", 
                          help="Estratégia de seleção de tópicos.")

    def handle(self, *args, **opts):
        Noticia = apps.get_model("rb_noticias", "Noticia")
        
        self.stdout.write("=== PUBLICAÇÃO INTELIGENTE DE TEMAS EM ASCENSÃO ===")
        self.stdout.write(f"Executado em: {timezone.now()}")
        self.stdout.write(f"Estratégia: {opts['strategy']}")
        self.stdout.write(f"Limite: {opts['limit']} artigos")

        # Inicializar analisadores
        enhanced_sources = EnhancedTrendingSources()
        audience_analyzer = AudienceAnalyzer()

        # Obter insights da audiência
        audience_insights = audience_analyzer.get_audience_insights()
        
        if opts["debug"]:
            self.stdout.write(self.style.NOTICE("=== INSIGHTS DA AUDIÊNCIA ==="))
            self.stdout.write(f"Top categorias: {audience_insights['top_categories']}")
            self.stdout.write(f"Palavras-chave trending: {audience_insights['trending_keywords']}")
            self.stdout.write(f"Melhores horários: {audience_insights['best_publishing_hours']}")

        # Selecionar estratégia de busca
        terms = []
        
        if opts["strategy"] == "trending":
            terms = self._get_enhanced_trending_topics(enhanced_sources, opts["limit"], opts)
        elif opts["strategy"] == "audience":
            # Priorizar fontes externas, fallback para audiência interna
            terms = self._get_enhanced_trending_topics(enhanced_sources, opts["limit"], opts)
            if len(terms) < opts["limit"]:
                audience_terms = self._get_audience_optimized_topics(audience_analyzer, opts["limit"] - len(terms))
                terms.extend(audience_terms)
        else:  # mixed
            terms = self._get_mixed_strategy_topics(enhanced_sources, audience_analyzer, opts["limit"], opts)

        # Remover duplicatas e limitar
        terms = list(dict.fromkeys(terms))[:opts["limit"]]

        if opts["debug"]:
            self.stdout.write(self.style.NOTICE(f"=== TÓPICOS SELECIONADOS ==="))
            for i, term in enumerate(terms, 1):
                prediction = audience_analyzer.predict_topic_success(term)
                self.stdout.write(f"{i}. {term} (Score: {prediction['success_score']:.1f})")

        if not terms:
            self.stdout.write(self.style.ERROR("Nenhum tópico encontrado."))
            return

        # Processar tópicos usando a MESMA LÓGICA do publish_topic
        created = 0
        
        for topic in terms:
            topic_clean = topic.strip()
            
            try:
                self.stdout.write(f"\n📝 Processando tema em ascensão: {topic_clean}")
                self.stdout.write(f"🔍 Sistema vai pesquisar '{topic_clean}' no Google News via navegador...")
                
                # Usar a mesma lógica do publish_topic (que já usa navegador + Google News)
                from django.core.management import call_command
                from io import StringIO
                import sys
                
                # Capturar output do publish_topic para análise
                old_stdout = sys.stdout
                sys.stdout = captured_output = StringIO()
                
                try:
                    # Chamar publish_topic com o tema encontrado
                    # O publish_topic já faz: busca RSS → navegador → extrai conteúdo → gera artigo
                    call_command('publish_topic', topic_clean, '--force')
                    
                    # Verificar se foi bem-sucedido analisando o output
                    output = captured_output.getvalue()
                    
                    if "✅" in output and ("Publicado" in output or "publicado" in output):
                        created += 1
                        self.stdout.write(self.style.SUCCESS(f"✅ Publicado: {topic_clean}"))
                        if opts["debug"]:
                            self.stdout.write(f"📄 Output: {output[:200]}...")
                    elif "❌" in output and "IA não atingiu critérios" in output:
                        self.stdout.write(f"⚠ Tema '{topic_clean}' não atingiu critérios de qualidade")
                    elif "❌" in output:
                        self.stdout.write(f"⚠ Falha na publicação de '{topic_clean}': {output[:100]}...")
                    else:
                        self.stdout.write(f"⚠ Resultado inesperado para '{topic_clean}'")
                        
                except Exception as e:
                    self.stdout.write(f"❌ Erro ao publicar {topic_clean}: {e}")
                    if opts["debug"]:
                        self.stdout.write(f"📄 Output capturado: {captured_output.getvalue()[:200]}...")
                    
                finally:
                    sys.stdout = old_stdout
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Erro ao processar {topic_clean}: {e}"))
                if opts["debug"]:
                    traceback.print_exc()
                continue

        self.stdout.write(self.style.SUCCESS(f"\n=== CONCLUÍDO ==="))
        self.stdout.write(f"Artigos publicados: {created}/{len(terms)}")
        
        if created > 0:
            self.stdout.write(self.style.SUCCESS("✅ Publicação inteligente concluída com sucesso!"))
        else:
            self.stdout.write(self.style.WARNING("⚠ Nenhum artigo foi publicado"))

    def _get_enhanced_trending_topics(self, enhanced_sources: EnhancedTrendingSources, limit: int, opts: dict) -> list:
        """Busca tópicos em ascensão usando fontes aprimoradas"""
        try:
            self.stdout.write("🔍 Buscando temas em ascensão de múltiplas fontes...")
            
            # Obter todos os trending topics
            trending_data = enhanced_sources.get_all_trending_topics(limit * 2)
            
            if not trending_data:
                self.stdout.write("⚠ Nenhum trending topic encontrado")
                return []
            
            # Extrair apenas os tópicos
            topics = []
            for item in trending_data[:limit]:
                topic = item.get('topic', '')
                if topic:
                    topics.append(topic)
                    if opts.get("debug", False):
                        source = item.get('source', 'unknown')
                        score = item.get('trend_score', 0)
                        category = item.get('category', 'geral')
                        self.stdout.write(f"  📈 {topic} (Fonte: {source}, Score: {score}, Categoria: {category})")
            
            self.stdout.write(f"✅ Encontrados {len(topics)} temas em ascensão")
            return topics
            
        except Exception as e:
            self.stdout.write(f"❌ Erro ao buscar trending topics: {e}")
            return []

    def _get_audience_optimized_topics(self, audience_analyzer: AudienceAnalyzer, limit: int) -> list:
        """Busca tópicos otimizados para a audiência atual"""
        try:
            self.stdout.write("🎯 Buscando tópicos otimizados para audiência...")
            
            insights = audience_analyzer.get_audience_insights()
            topics = []
            
            # Usar palavras-chave trending da audiência (filtrar genéricas e priorizar temas brasileiros)
            for keyword in insights.get('trending_keywords', []):
                if (len(keyword) > 3 and 
                    keyword not in ['sobre', 'análise', 'notícia', 'brasil', 'trump', 'usa', 'america'] and
                    not keyword.isupper()):  # Evitar siglas
                    topics.append(keyword)
                    if len(topics) >= limit:
                        break
            
            # Se não tiver palavras-chave suficientes, usar categorias de alto desempenho
            if len(topics) < limit:
                for category in insights.get('top_categories', []):
                    if len(topics) >= limit:
                        break
                    topics.append(f"notícias {category}")
            
            # Fallback com tópicos relevantes se ainda não tiver o suficiente
            if len(topics) < limit:
                fallback_topics = [
                    "inflação Brasil", "economia brasileira", "política nacional",
                    "tecnologia Brasil", "saúde pública", "meio ambiente"
                ]
                for topic in fallback_topics:
                    if len(topics) >= limit:
                        break
                    if topic not in topics:
                        topics.append(topic)
            
            self.stdout.write(f"✅ Encontrados {len(topics)} tópicos otimizados")
            return topics
            
        except Exception as e:
            self.stdout.write(f"❌ Erro ao buscar tópicos otimizados: {e}")
            # Fallback com tópicos relevantes
            return ["inflação Brasil", "economia brasileira", "política nacional"][:limit]

    def _get_mixed_strategy_topics(self, enhanced_sources: EnhancedTrendingSources, 
                                 audience_analyzer: AudienceAnalyzer, limit: int, opts: dict) -> list:
        """Combina estratégias de trending topics e análise de audiência"""
        # 60% trending topics, 40% audience optimized
        trending_count = int(limit * 0.6)
        audience_count = limit - trending_count
        
        trending_topics = self._get_enhanced_trending_topics(enhanced_sources, trending_count, opts)
        audience_topics = self._get_audience_optimized_topics(audience_analyzer, audience_count)
        
        return trending_topics + audience_topics
