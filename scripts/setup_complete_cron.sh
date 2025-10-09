#!/bin/bash
# Configuração completa de cron jobs para RadarBR
# Sistema de automação periódica inteligente

echo "=== CONFIGURAÇÃO CRON JOBS RADARBR ==="

# Criar diretório de logs se não existir
mkdir -p /opt/render/project/logs

# Backup do crontab atual
echo "Fazendo backup do crontab atual..."
crontab -l > /opt/render/project/crontab_backup_$(date +%Y%m%d_%H%M).txt 2>/dev/null || echo "# Crontab backup" > /opt/render/project/crontab_backup.txt

# Configurar novos cron jobs
echo "Configurando cron jobs..."
cat > /opt/render/project/crontab_new.txt << 'EOF'
# ========================================
# CRON JOBS RADARBR - AUTOMAÇÃO PERIÓDICA
# ========================================

# Monitoramento a cada 30 minutos
*/30 * * * * bash /opt/render/project/src/scripts/monitor_automation.sh >> /opt/render/project/logs/monitor.log 2>&1

# Agendamento inteligente a cada 2 horas
0 */2 * * * bash /opt/render/project/src/scripts/smart_scheduler.sh >> /opt/render/project/logs/scheduler.log 2>&1

# Automação completa a cada 6 horas
0 */6 * * * bash /opt/render/project/src/scripts/full_automation.sh >> /opt/render/project/logs/automation.log 2>&1

# Ping sitemap a cada 4 horas
0 */4 * * * cd /opt/render/project/src && source .venv/bin/activate && python manage.py ping_sitemap >> /opt/render/project/logs/sitemap.log 2>&1

# Limpeza de logs semanalmente (domingos às 2h)
0 2 * * 0 find /opt/render/project/logs -name "*.log" -mtime +7 -delete

# Backup semanal do banco (domingos às 3h)
0 3 * * 0 cd /opt/render/project/src && source .venv/bin/activate && python manage.py dumpdata --indent 2 --output /opt/render/project/backups/backup_$(date +\%Y\%m\%d).json >> /opt/render/project/logs/backup.log 2>&1

# Verificação de saúde do sistema diariamente (6h)
0 6 * * * bash /opt/render/project/src/scripts/health_check.sh >> /opt/render/project/logs/health.log 2>&1
EOF

# Instalar novo crontab
echo "Instalando novo crontab..."
crontab /opt/render/project/crontab_new.txt

# Verificar se foi instalado
echo "Verificando cron jobs instalados:"
crontab -l

# Criar diretório de backups
mkdir -p /opt/render/project/backups

# Criar script de verificação de saúde
cat > /opt/render/project/src/scripts/health_check.sh << 'EOF'
#!/bin/bash
# Verificação de saúde do sistema RadarBR

echo "=== HEALTH CHECK RADARBR ==="
echo "Verificação em: $(date)"

cd /opt/render/project/src
source .venv/bin/activate

# Verificar Django
if python manage.py check; then
    echo "✅ Django OK"
else
    echo "❌ Django com problemas"
fi

# Verificar banco de dados
if python manage.py shell -c "from django.db import connection; connection.cursor()"; then
    echo "✅ Banco de dados OK"
else
    echo "❌ Banco de dados com problemas"
fi

# Verificar arquivos estáticos
if [ -d "/opt/render/project/src/staticfiles" ]; then
    echo "✅ Arquivos estáticos OK"
else
    echo "❌ Arquivos estáticos faltando"
fi

# Verificar espaço em disco
disk_usage=$(df -h /opt/render/project | tail -1 | awk '{print $5}' | sed 's/%//')
echo "💾 Uso de disco: ${disk_usage}%"

if [ "$disk_usage" -gt 90 ]; then
    echo "⚠️ Espaço em disco crítico!"
fi

echo "=== HEALTH CHECK CONCLUÍDO ==="
EOF

chmod +x /opt/render/project/src/scripts/health_check.sh

echo ""
echo "=== CONFIGURAÇÃO CONCLUÍDA ==="
echo "📋 Cron jobs configurados:"
echo "  • Monitoramento: a cada 30 minutos"
echo "  • Agendamento inteligente: a cada 2 horas"
echo "  • Automação completa: a cada 6 horas"
echo "  • Ping sitemap: a cada 4 horas"
echo "  • Limpeza de logs: semanalmente"
echo "  • Backup do banco: semanalmente"
echo "  • Verificação de saúde: diariamente"
echo ""
echo "📁 Logs serão salvos em: /opt/render/project/logs/"
echo "💾 Backups serão salvos em: /opt/render/project/backups/"
echo ""
echo "🔍 Para monitorar logs:"
echo "  tail -f /opt/render/project/logs/monitor.log"
echo "  tail -f /opt/render/project/logs/automation.log"
echo "  tail -f /opt/render/project/logs/scheduler.log"
echo ""
echo "✅ Sistema de automação periódica configurado!"
