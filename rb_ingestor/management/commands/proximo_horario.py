# rb_ingestor/management/commands/proximo_horario.py
"""
Comando para calcular o próximo horário de publicação automática
"""
from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
import pytz

class Command(BaseCommand):
    help = "Calcula o próximo horário de publicação automática"

    def handle(self, *args, **options):
        self.stdout.write("=== HORARIOS DE PUBLICACAO AUTOMATICA ===")
        
        # Horários configurados no render.yaml
        horarios_principais = [8, 12, 15, 18, 20]  # Horários otimizados
        horarios_fallback = "*/2"  # A cada 2 horas
        horarios_automation = "*/6"  # A cada 6 horas
        
        # Fuso horário do Brasil (UTC-3)
        brasil_tz = pytz.timezone('America/Sao_Paulo')
        agora_brasil = datetime.now(brasil_tz)
        
        self.stdout.write(f"Hora atual no Brasil: {agora_brasil.strftime('%H:%M')}")
        self.stdout.write(f"Data atual: {agora_brasil.strftime('%d/%m/%Y')}")
        
        # Calcular próximo horário principal
        proximo_horario = None
        proxima_data = agora_brasil.date()
        
        # Verificar se ainda há horários hoje
        for hora in horarios_principais:
            if hora > agora_brasil.hour:
                proximo_horario = hora
                proxima_data = agora_brasil.date()
                break
        
        # Se não há mais horários hoje, pegar o primeiro de amanhã
        if proximo_horario is None:
            proximo_horario = horarios_principais[0]
            proxima_data = agora_brasil.date() + timedelta(days=1)
        
        # Criar datetime do próximo horário
        proximo_datetime = brasil_tz.localize(
            datetime.combine(proxima_data, datetime.min.time().replace(hour=proximo_horario))
        )
        
        # Calcular tempo restante
        tempo_restante = proximo_datetime - agora_brasil
        
        self.stdout.write("\n=== PROXIMO HORARIO DE PUBLICACAO ===")
        self.stdout.write(f"Horario: {proximo_datetime.strftime('%H:%M')}")
        self.stdout.write(f"Data: {proximo_datetime.strftime('%d/%m/%Y')}")
        self.stdout.write(f"Tempo restante: {self._format_timedelta(tempo_restante)}")
        
        # Mostrar todos os horários de hoje
        self.stdout.write("\n=== HORARIOS DE HOJE ===")
        hoje = agora_brasil.date()
        horarios_hoje = []
        
        for hora in horarios_principais:
            horario_hoje = brasil_tz.localize(
                datetime.combine(hoje, datetime.min.time().replace(hour=hora))
            )
            if horario_hoje > agora_brasil:
                horarios_hoje.append(horario_hoje)
        
        if horarios_hoje:
            for horario in horarios_hoje:
                tempo_rest = horario - agora_brasil
                status = "PROXIMO" if horario == proximo_datetime else "Aguardando"
                self.stdout.write(f"  {horario.strftime('%H:%M')} - {status} ({self._format_timedelta(tempo_rest)})")
        else:
            self.stdout.write("  Nenhum horário restante hoje")
        
        # Mostrar horários de amanhã
        self.stdout.write("\n=== HORARIOS DE AMANHA ===")
        amanha = hoje + timedelta(days=1)
        for hora in horarios_principais:
            horario_amanha = brasil_tz.localize(
                datetime.combine(amanha, datetime.min.time().replace(hour=hora))
            )
            tempo_rest = horario_amanha - agora_brasil
            self.stdout.write(f"  {horario_amanha.strftime('%H:%M')} - {self._format_timedelta(tempo_rest)}")
        
        # Informações sobre os sistemas
        self.stdout.write("\n=== SISTEMAS DE AUTOMACAO ===")
        self.stdout.write("1. Sistema Principal (smart_automation): 8h, 12h, 15h, 18h, 20h")
        self.stdout.write("2. Sistema Fallback (smart_scheduler): A cada 2 horas")
        self.stdout.write("3. Sistema Automation: A cada 6 horas")
        self.stdout.write("4. Monitor Performance: 6h (diário)")
        
        # Status atual
        self.stdout.write(f"\n=== STATUS ATUAL ===")
        self.stdout.write(f"Proxima publicacao: {proximo_datetime.strftime('%d/%m/%Y às %H:%M')}")
        self.stdout.write(f"Tempo restante: {self._format_timedelta(tempo_restante)}")
        
        if tempo_restante.total_seconds() < 3600:  # Menos de 1 hora
            self.stdout.write(self.style.SUCCESS("OK Publicacao proxima!"))
        elif tempo_restante.total_seconds() < 7200:  # Menos de 2 horas
            self.stdout.write(self.style.WARNING("AVISO Publicacao em breve"))
        else:
            self.stdout.write("Aguardando proxima publicacao")
    
    def _format_timedelta(self, td):
        """Formata timedelta em formato legível"""
        total_seconds = int(td.total_seconds())
        
        if total_seconds < 0:
            return "Já passou"
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}h {minutes}min"
        else:
            return f"{minutes}min"
