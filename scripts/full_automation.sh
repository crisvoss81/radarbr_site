#!/bin/bash
# Script de automação completa para RadarBR
# Executa busca de tópicos, geração de notícias e publicação automaticamente

echo "=== AUTOMAÇÃO COMPLETA RADARBR ==="
echo "Iniciado em: $(date)"

# Mudar para o diretório do projeto
cd /opt/render/project/src

# Ativar ambiente virtual
source .venv/bin/activate

# Função para log com timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Função para executar comando com retry
execute_with_retry() {
    local cmd="$1"
    local max_attempts=3
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log "Tentativa $attempt de $max_attempts: $cmd"
        
        if eval "$cmd"; then
            log "✅ Comando executado com sucesso"
            return 0
        else
            log "❌ Falha na tentativa $attempt"
            attempt=$((attempt + 1))
            sleep 5
        fi
    done
    
    log "❌ Comando falhou após $max_attempts tentativas"
    return 1
}

# 1. Verificar notícias recentes
log "Verificando notícias recentes..."
python manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from rb_noticias.models import Noticia

total = Noticia.objects.count()
recentes = Noticia.objects.filter(
    criado_em__gte=timezone.now() - timedelta(hours=6)
).count()

print(f'Total notícias: {total}')
print(f'Últimas 6h: {recentes}')

if recentes < 2:
    print('EXECUTE_AUTOMATION')
else:
    print('SKIP_AUTOMATION')
"

# Capturar resultado da verificação
check_result=$(python manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from rb_noticias.models import Noticia

recentes = Noticia.objects.filter(
    criado_em__gte=timezone.now() - timedelta(hours=6)
).count()

if recentes < 2:
    print('EXECUTE_AUTOMATION')
else:
    print('SKIP_AUTOMATION')
" | tail -1)

if [ "$check_result" = "EXECUTE_AUTOMATION" ]; then
    log "⚠️ Poucas notícias recentes - executando automação completa..."
    
    # 2. Executar busca de tópicos trending
    log "🔍 Buscando tópicos trending..."
    execute_with_retry "python manage.py smart_trends_publish --strategy trending --limit 2 --force"
    
    # 3. Executar busca baseada na audiência
    log "👥 Buscando tópicos baseados na audiência..."
    execute_with_retry "python manage.py smart_trends_publish --strategy audience --limit 2 --force"
    
    # 4. Executar estratégia mista
    log "🎯 Executando estratégia mista..."
    execute_with_retry "python manage.py smart_trends_publish --strategy mixed --limit 3 --force"
    
    # 5. Verificar resultados
    log "📊 Verificando resultados..."
    python manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from rb_noticias.models import Noticia

total = Noticia.objects.count()
recentes = Noticia.objects.filter(
    criado_em__gte=timezone.now() - timedelta(hours=1)
).count()

print(f'Total notícias: {total}')
print(f'Novas notícias (última hora): {recentes}')
"
    
    # 6. Ping sitemap
    log "🗺️ Atualizando sitemap..."
    execute_with_retry "python manage.py ping_sitemap"
    
    log "✅ Automação completa executada com sucesso!"
    
else
    log "✅ Quantidade adequada de notícias recentes - pulando automação"
fi

# 7. Mostrar estatísticas finais
log "📈 Estatísticas finais:"
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

print(f'Total: {total} notícias')
print(f'Hoje: {hoje} notícias')
print(f'Última hora: {ultima_hora} notícias')
"

# 8. Mostrar últimas notícias
log "📰 Últimas 5 notícias:"
python manage.py shell -c "
from rb_noticias.models import Noticia
for n in Noticia.objects.order_by('-criado_em')[:5]:
    print(f'- {n.titulo} ({n.criado_em.strftime(\"%H:%M\")})')
"

log "=== AUTOMAÇÃO CONCLUÍDA ==="
echo "Finalizado em: $(date)"
