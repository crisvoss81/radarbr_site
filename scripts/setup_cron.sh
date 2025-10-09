#!/bin/bash
# Script para configurar cron jobs no Render

echo "=== CONFIGURANDO CRON JOBS NO RENDER ==="

# Criar diretório de logs se não existir
mkdir -p /opt/render/project/logs

# Configurar cron jobs
echo "Configurando cron jobs..."

# Backup do crontab atual
crontab -l > /opt/render/project/crontab_backup.txt 2>/dev/null || echo "# Crontab backup" > /opt/render/project/crontab_backup.txt

# Adicionar novos cron jobs
cat > /opt/render/project/crontab_new.txt << 'EOF'
# Cron jobs para RadarBR
# Executar verificação de automação a cada 6 horas
0 */6 * * * bash /opt/render/project/src/scripts/check_automation_simple.sh >> /opt/render/project/logs/cron.log 2>&1

# Ping sitemap a cada 4 horas  
0 */4 * * * cd /opt/render/project/src && source .venv/bin/activate && python manage.py ping_sitemap >> /opt/render/project/logs/cron.log 2>&1

# Limpeza de logs semanalmente (domingos às 2h)
0 2 * * 0 find /opt/render/project/logs -name "*.log" -mtime +7 -delete
EOF

# Instalar novo crontab
crontab /opt/render/project/crontab_new.txt

# Verificar se foi instalado
echo "Cron jobs configurados:"
crontab -l

echo "=== CONFIGURAÇÃO CONCLUÍDA ==="
echo "Logs serão salvos em: /opt/render/project/logs/cron.log"
echo "Para verificar logs: tail -f /opt/render/project/logs/cron.log"
