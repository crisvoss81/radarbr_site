# rb_ingestor/management/commands/check_publication.py
"""
Comando para verificar se as notícias estão sendo publicadas
"""
from django.core.management.base import BaseCommand
from rb_noticias.models import Noticia
from rb_ingestor.trending_analyzer_real import RealTrendingAnalyzer
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = "Verifica se as notícias estão sendo publicadas com os tópicos encontrados"

    def handle(self, *args, **options):
        self.stdout.write("=== VERIFICAÇÃO DE PUBLICAÇÃO ===")
        
        # 1. Verificar notícias recentes
        recent_count = Noticia.objects.filter(
            criado_em__gte=timezone.now() - timedelta(hours=2)
        ).count()
        
        self.stdout.write(f"📊 Notícias últimas 2h: {recent_count}")
        
        if recent_count > 0:
            latest = Noticia.objects.latest('criado_em')
            self.stdout.write(f"📰 Última notícia: {latest.titulo}")
            self.stdout.write(f"🏷️  Categoria: {latest.categoria.nome if latest.categoria else 'Sem categoria'}")
            self.stdout.write(f"🔗 Fonte: {latest.fonte_nome}")
            self.stdout.write(f"🕒 Data: {latest.criado_em}")
        
        # 2. Verificar tópicos disponíveis
        self.stdout.write("\n=== TÓPICOS DISPONÍVEIS ===")
        
        try:
            analyzer = RealTrendingAnalyzer()
            topics = analyzer.get_cached_trends()
            
            self.stdout.write(f"📈 Tópicos encontrados: {len(topics)}")
            
            for i, topic in enumerate(topics[:5], 1):
                self.stdout.write(f"{i}. {topic['topic']} ({topic['source']})")
                
        except Exception as e:
            self.stdout.write(f"❌ Erro ao buscar tópicos: {e}")
        
        # 3. Verificar sistema de automação
        self.stdout.write("\n=== SISTEMA DE AUTOMAÇÃO ===")
        
        # Verificar se está usando tópicos reais ou fixos
        from rb_ingestor.management.commands.automacao_render import Command as AutoCommand
        auto_cmd = AutoCommand()
        
        try:
            topics = auto_cmd._get_topics()
            self.stdout.write(f"🎯 Tópicos do sistema atual: {len(topics)}")
            for topic in topics:
                self.stdout.write(f"   - {topic}")
        except Exception as e:
            self.stdout.write(f"❌ Erro no sistema atual: {e}")
        
        self.stdout.write("\n=== CONCLUSÃO ===")
        
        if recent_count > 0:
            self.stdout.write("✅ Sistema está publicando notícias")
        else:
            self.stdout.write("❌ Sistema não está publicando")
            
        if len(topics) > 0:
            self.stdout.write("✅ Sistema está encontrando tópicos")
        else:
            self.stdout.write("❌ Sistema não está encontrando tópicos")
