#!/bin/bash
# Script de automação simplificado para Render
# Versão robusta que funciona mesmo com limitações de recursos

set -e

echo "=== AUTOMACAO RENDER RADARBR ==="
echo "Executado em: $(date)"
echo "Diretório: $(pwd)"

# Mudar para o diretório do projeto
cd /opt/render/project/src

# Ativar ambiente virtual se existir
if [ -d ".venv" ]; then
    echo "Ativando ambiente virtual..."
    source .venv/bin/activate
fi

# Função para log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Verificar se Django está funcionando
log "Verificando Django..."
python manage.py check --deploy

# Executar migrações se necessário
log "Verificando migrações..."
python manage.py migrate --noinput

# Executar automação com fallbacks
log "Executando automação..."

# Tentar comando principal primeiro
if python manage.py automacao_render --limit 3; then
    log "✅ Automação principal executada com sucesso"
elif python manage.py automacao_simples --limit 3 --force; then
    log "✅ Automação simples executada com sucesso (fallback 1)"
elif python manage.py auto_publish --quick --limit 2; then
    log "✅ Auto publish executado com sucesso (fallback 2)"
else
    log "❌ Todos os comandos de automação falharam"
    exit 1
fi

# Coletar arquivos estáticos
log "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Ping sitemap
log "Fazendo ping do sitemap..."
python manage.py ping_sitemap || log "⚠ Ping sitemap falhou, continuando..."

# Mostrar estatísticas
log "📊 Estatísticas:"
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

log "=== AUTOMACAO CONCLUIDA ==="
