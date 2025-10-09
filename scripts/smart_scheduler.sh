#!/bin/bash
# Sistema de agendamento inteligente para RadarBR
# Executa automação em horários estratégicos baseados na audiência

echo "=== AGENDAMENTO INTELIGENTE RADARBR ==="
echo "Executado em: $(date)"

# Mudar para o diretório do projeto
cd /opt/render/project/src
source .venv/bin/activate

# Função para log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Obter hora atual
current_hour=$(date +%H)
current_day=$(date +%u)  # 1=segunda, 7=domingo

log "Hora atual: $current_hour"
log "Dia da semana: $current_day"

# Definir estratégias baseadas no horário
case $current_hour in
    06|07|08)
        strategy="trending"
        limit=3
        log "🌅 Manhã - Estratégia trending (3 notícias)"
        ;;
    09|10|11)
        strategy="audience"
        limit=4
        log "☀️ Manhã tardia - Estratégia audience (4 notícias)"
        ;;
    12|13|14)
        strategy="mixed"
        limit=5
        log "🌞 Almoço - Estratégia mista (5 notícias)"
        ;;
    15|16|17)
        strategy="audience"
        limit=4
        log "🌤️ Tarde - Estratégia audience (4 notícias)"
        ;;
    18|19|20)
        strategy="mixed"
        limit=6
        log "🌆 Noite - Estratégia mista (6 notícias - horário de pico)"
        ;;
    21|22|23)
        strategy="trending"
        limit=3
        log "🌙 Noite tardia - Estratégia trending (3 notícias)"
        ;;
    *)
        strategy="trending"
        limit=2
        log "🌃 Madrugada - Estratégia trending (2 notícias)"
        ;;
esac

# Verificar se é fim de semana (sábado=6, domingo=7)
if [ $current_day -eq 6 ] || [ $current_day -eq 7 ]; then
    limit=$((limit + 1))
    log "📅 Fim de semana - Aumentando limite para $limit"
fi

# Verificar notícias recentes
log "Verificando notícias recentes..."
recent_count=$(python manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from rb_noticias.models import Noticia

recentes = Noticia.objects.filter(
    criado_em__gte=timezone.now() - timedelta(hours=3)
).count()

print(recentes)
" | tail -1)

log "Notícias recentes (3h): $recent_count"

# Se há poucas notícias recentes, executar automação
if [ "$recent_count" -lt 2 ]; then
    log "⚠️ Poucas notícias recentes - executando automação..."
    
    # Executar comando de publicação
    log "🚀 Executando: smart_trends_publish --strategy $strategy --limit $limit"
    
    # Sistema inteligente de automação com fallbacks
    if python manage.py smart_automation --mode auto; then
        log "✅ Sistema inteligente executado com sucesso"
    elif python manage.py smart_trends_publish --strategy "$strategy" --limit "$limit" --force; then
        log "✅ Comando smart_trends_publish executado com sucesso (fallback 1)"
    elif python manage.py automacao_simples --limit "$limit" --force; then
        log "✅ Comando automacao_simples executado com sucesso (fallback 2)"
    else
        log "❌ Erro na publicação - todos os comandos falharam"
        exit 1
    fi
    
    # Ping sitemap após publicação bem-sucedida
    log "🗺️ Atualizando sitemap..."
    python manage.py ping_sitemap
        
    # Mostrar estatísticas
    log "📊 Estatísticas pós-publicação:"
    python manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from rb_noticias.models import Noticia

total = Noticia.objects.count()
recentes = Noticia.objects.filter(
    criado_em__gte=timezone.now() - timedelta(hours=1)
).count()

print(f'Total: {total} notícias')
print(f'Última hora: {recentes} notícias')
"
    
else
    log "✅ Quantidade adequada de notícias recentes - pulando automação"
fi

log "=== AGENDAMENTO CONCLUÍDO ==="
