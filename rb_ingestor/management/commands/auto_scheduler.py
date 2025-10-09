# rb_ingestor/management/commands/auto_scheduler.py
"""
Comando Django para execução automática periódica
Sistema inteligente de busca e publicação de notícias
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, datetime
from rb_noticias.models import Noticia
from django.core.management import call_command
import logging

# Configurar logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Executa automação periódica inteligente de notícias"

    def add_arguments(self, parser):
        parser.add_argument(
            '--mode',
            choices=['monitor', 'schedule', 'full'],
            default='schedule',
            help='Modo de execução: monitor, schedule ou full'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força execução mesmo com publicações recentes'
        )

    def get_time_strategy(self):
        """Determina estratégia baseada no horário atual"""
        now = timezone.now()
        hour = now.hour
        weekday = now.weekday()  # 0=segunda, 6=domingo
        
        # Estratégias baseadas no horário
        if 6 <= hour < 12:  # Manhã
            return "trending", 3, "🌅 Manhã"
        elif 12 <= hour < 18:  # Tarde
            return "audience", 4, "☀️ Tarde"
        elif 18 <= hour < 22:  # Noite (horário de pico)
            return "mixed", 6, "🌆 Noite (pico)"
        else:  # Madrugada
            return "trending", 2, "🌃 Madrugada"
    
    def check_recent_publications(self, hours=3):
        """Verifica publicações recentes"""
        cutoff_time = timezone.now() - timedelta(hours=hours)
        return Noticia.objects.filter(criado_em__gte=cutoff_time).count()
    
    def execute_automation(self, strategy, limit, description):
        """Executa automação com estratégia específica"""
        try:
            self.stdout.write(f"🚀 Executando: {description}")
            self.stdout.write(f"   Estratégia: {strategy}, Limite: {limit}")
            
            call_command(
                'smart_trends_publish',
                '--strategy', strategy,
                '--limit', str(limit),
                '--force'
            )
            
            self.stdout.write(self.style.SUCCESS("✅ Publicação executada com sucesso!"))
            return True
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro na publicação: {str(e)}"))
            return False
    
    def monitor_mode(self):
        """Modo de monitoramento - verifica e executa se necessário"""
        self.stdout.write("📊 MODO MONITORAMENTO")
        
        recent_count = self.check_recent_publications(3)
        self.stdout.write(f"Notícias recentes (3h): {recent_count}")
        
        if recent_count < 2:
            self.stdout.write(self.style.WARNING("⚠️ Poucas notícias recentes - executando automação rápida"))
            strategy, limit, description = self.get_time_strategy()
            return self.execute_automation(strategy, limit, description)
        else:
            self.stdout.write(self.style.SUCCESS("✅ Sistema funcionando normalmente"))
            return True
    
    def schedule_mode(self):
        """Modo de agendamento - execução inteligente baseada no horário"""
        self.stdout.write("⏰ MODO AGENDAMENTO")
        
        if not self.options['force']:
            recent_count = self.check_recent_publications(3)
            if recent_count >= 2:
                self.stdout.write(self.style.SUCCESS("✅ Quantidade adequada de notícias recentes"))
                return True
        
        strategy, limit, description = self.get_time_strategy()
        
        # Ajustar limite para fim de semana
        if timezone.now().weekday() >= 5:  # Sábado ou domingo
            limit += 1
            description += " (fim de semana)"
        
        return self.execute_automation(strategy, limit, description)
    
    def full_mode(self):
        """Modo completo - execução de múltiplas estratégias"""
        self.stdout.write("🔄 MODO COMPLETO")
        
        strategies = [
            ("trending", 2, "🔍 Trending topics"),
            ("audience", 2, "👥 Baseado na audiência"),
            ("mixed", 3, "🎯 Estratégia mista")
        ]
        
        success_count = 0
        for strategy, limit, description in strategies:
            if self.execute_automation(strategy, limit, description):
                success_count += 1
        
        self.stdout.write(f"📊 Resultado: {success_count}/{len(strategies)} estratégias executadas com sucesso")
        return success_count > 0
    
    def handle(self, *args, **options):
        try:
            mode = options['mode']
            self.stdout.write(f"=== AUTOMAÇÃO PERIÓDICA - MODO {mode.upper()} ===")
            self.stdout.write(f"Iniciado em: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Executar modo específico
            if mode == 'monitor':
                success = self.monitor_mode()
            elif mode == 'schedule':
                success = self.schedule_mode()
            elif mode == 'full':
                success = self.full_mode()
            
            # Estatísticas finais
            total_news = Noticia.objects.count()
            recent_news = Noticia.objects.filter(
                criado_em__gte=timezone.now() - timedelta(hours=1)
            ).count()
            
            self.stdout.write(f"\n📈 Estatísticas:")
            self.stdout.write(f"   Total: {total_news} notícias")
            self.stdout.write(f"   Última hora: {recent_news} notícias")
            
            # Ping sitemap se houve sucesso
            if success:
                self.stdout.write("🗺️ Atualizando sitemap...")
                try:
                    call_command('ping_sitemap')
                    self.stdout.write(self.style.SUCCESS("✅ Sitemap atualizado"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Erro no sitemap: {str(e)}"))
            
            self.stdout.write(f"\n=== AUTOMAÇÃO CONCLUÍDA ===")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro geral: {str(e)}"))
            raise
