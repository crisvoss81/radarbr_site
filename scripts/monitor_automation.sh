#!/bin/bash
# Sistema de monitoramento para automação RadarBR
# Verifica status da execução e gera relatórios

echo "=== MONITORAMENTO AUTOMAÇÃO RADARBR ==="
echo "Verificação em: $(date)"

# Mudar para o diretório do projeto
cd /opt/render/project/src
source .venv/bin/activate

# Função para log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Criar diretório de logs se não existir
mkdir -p /opt/render/project/logs

# Arquivo de log do monitoramento
MONITOR_LOG="/opt/render/project/logs/monitor.log"

# Função para adicionar ao log
add_to_log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$MONITOR_LOG"
}

# 1. Verificar status geral
log "📊 Verificando status geral..."
python manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from rb_noticias.models import Noticia

total = Noticia.objects.count()
hoje = Noticia.objects.filter(
    criado_em__gte=timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
).count()
ultima_hora = Noticia.objects.filter(
    criado_em__gte=timezone.now() - timedelta(hours=1)
).count()
ultimas_6h = Noticia.objects.filter(
    criado_em__gte=timezone.now() - timedelta(hours=6)
).count()

print(f'STATUS: Total={total}, Hoje={hoje}, Última_hora={ultima_hora}, Últimas_6h={ultimas_6h}')
" > /tmp/status.txt

# Ler status
status=$(cat /tmp/status.txt | tail -1)
log "Status: $status"
add_to_log "STATUS_CHECK: $status"

# 2. Verificar última execução de automação
log "🕐 Verificando última execução..."
last_automation=$(python manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from rb_noticias.models import Noticia

try:
    ultima = Noticia.objects.order_by('-criado_em').first()
    if ultima:
        diff = timezone.now() - ultima.criado_em
        hours_ago = diff.total_seconds() / 3600
        print(f'Última notícia: {ultima.titulo[:50]}... ({hours_ago:.1f}h atrás)')
    else:
        print('Nenhuma notícia encontrada')
except Exception as e:
    print(f'Erro: {str(e)}')
" | tail -1)

log "Última execução: $last_automation"
add_to_log "LAST_EXECUTION: $last_automation"

# 3. Verificar se precisa executar automação
log "🔍 Verificando necessidade de automação..."
need_automation=$(python manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from rb_noticias.models import Noticia

recentes = Noticia.objects.filter(
    criado_em__gte=timezone.now() - timedelta(hours=3)
).count()

if recentes < 2:
    print('NEED_AUTOMATION')
else:
    print('OK')
" | tail -1)

if [ "$need_automation" = "NEED_AUTOMATION" ]; then
    log "⚠️ AUTOMAÇÃO NECESSÁRIA!"
    add_to_log "ALERT: Automation needed"
    
    # Executar automação rápida
    log "🚀 Executando automação rápida..."
    if python manage.py check_and_publish --min-count 2 --publish-count 3; then
        log "✅ Automação executada com sucesso!"
        add_to_log "SUCCESS: Quick automation executed"
    else
        log "❌ Falha na automação!"
        add_to_log "ERROR: Automation failed"
    fi
else
    log "✅ Sistema funcionando normalmente"
    add_to_log "OK: System running normally"
fi

# 4. Verificar logs de erro
log "🔍 Verificando logs de erro..."
if [ -f "/opt/render/project/logs/cron.log" ]; then
    error_count=$(grep -c "ERROR\|❌\|Failed" /opt/render/project/logs/cron.log 2>/dev/null || echo "0")
    log "Erros encontrados nos logs: $error_count"
    add_to_log "ERROR_COUNT: $error_count"
    
    if [ "$error_count" -gt 0 ]; then
        log "⚠️ Erros detectados nos logs!"
        add_to_log "ALERT: Errors in logs"
    fi
else
    log "📝 Arquivo de log não encontrado"
    add_to_log "INFO: Log file not found"
fi

# 5. Verificar espaço em disco
log "💾 Verificando espaço em disco..."
disk_usage=$(df -h /opt/render/project | tail -1 | awk '{print $5}' | sed 's/%//')
log "Uso de disco: ${disk_usage}%"
add_to_log "DISK_USAGE: ${disk_usage}%"

if [ "$disk_usage" -gt 80 ]; then
    log "⚠️ Espaço em disco baixo!"
    add_to_log "ALERT: Low disk space"
fi

# 6. Gerar relatório resumido
log "📋 Gerando relatório..."
echo "=== RELATÓRIO DE MONITORAMENTO ===" > /tmp/monitor_report.txt
echo "Data: $(date)" >> /tmp/monitor_report.txt
echo "Status: $status" >> /tmp/monitor_report.txt
echo "Última execução: $last_automation" >> /tmp/monitor_report.txt
echo "Necessita automação: $need_automation" >> /tmp/monitor_report.txt
echo "Erros nos logs: $error_count" >> /tmp/monitor_report.txt
echo "Uso de disco: ${disk_usage}%" >> /tmp/monitor_report.txt

# Mostrar relatório
cat /tmp/monitor_report.txt

# Salvar relatório
cp /tmp/monitor_report.txt "/opt/render/project/logs/monitor_report_$(date +%Y%m%d_%H%M).txt"

log "=== MONITORAMENTO CONCLUÍDO ==="
add_to_log "MONITORING_COMPLETED"
