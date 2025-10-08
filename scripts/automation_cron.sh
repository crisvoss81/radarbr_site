#!/bin/bash
# Script de automação para RadarBR
# Executa publicação automática de notícias

# Configurações
PROJECT_DIR="/opt/render/project/src"
LOG_FILE="/opt/render/project/logs/automation.log"

# Criar diretório de logs se não existir
mkdir -p /opt/render/project/logs

# Função de log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Entrar no diretório do projeto
cd "$PROJECT_DIR" || exit 1

# Ativar ambiente virtual
source .venv/bin/activate

# Executar automação
log "Iniciando automação de notícias..."
python manage.py auto_publish --strategy mixed --limit 3

if [ $? -eq 0 ]; then
    log "Automação executada com sucesso"
else
    log "Erro na execução da automação"
fi

# Ping sitemap
log "Enviando ping para sitemap..."
python manage.py ping_sitemap

log "Script de automação concluído"
