#!/bin/bash
# Script de automação para Render
# Executa publicação inteligente de notícias

set -e

echo "=== INICIANDO AUTOMAÇÃO RADARBR ==="
echo "Data/Hora: $(date)"
echo "Diretório: $(pwd)"

# Ativar ambiente virtual se existir
if [ -d ".venv" ]; then
    echo "Ativando ambiente virtual..."
    source .venv/bin/activate
fi

# Executar migrações se necessário
echo "Verificando migrações..."
python manage.py migrate --noinput

# Executar comando de automação
echo "Executando automação de notícias..."
python manage.py auto_publish

# Coletar arquivos estáticos
echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Ping sitemap
echo "Fazendo ping do sitemap..."
python manage.py ping_sitemap || echo "Ping sitemap falhou, continuando..."

echo "=== AUTOMAÇÃO CONCLUÍDA ==="
