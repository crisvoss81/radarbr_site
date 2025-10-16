#!/bin/bash
# Script para build completo do projeto

echo "=== BUILD RADARBR ==="

# 1. Ativar ambiente virtual (se existir)
if [ -d ".venv" ]; then
    echo "Ativando ambiente virtual..."
    source .venv/bin/activate 2>/dev/null || .venv/Scripts/activate 2>/dev/null
fi

# 2. Instalar dependências Python
echo "Instalando dependências Python..."
pip install -r requirements.txt

# 2.1. Instalar browsers do Playwright
echo "Instalando browsers do Playwright..."
# Garante instalação dentro do projeto (persistente no deploy)
export PLAYWRIGHT_BROWSERS_PATH=0
# Instala chromium-headless-shell primeiro (preferido), depois chromium como fallback
echo "Instalando chromium-headless-shell..."
python -m playwright install chromium-headless-shell || echo "⚠ chromium-headless-shell falhou, tentando chromium..."
python -m playwright install chromium
echo "Verificando instalação do Chromium..."
python -c "
from playwright.sync_api import sync_playwright
p = sync_playwright().start()
try:
    browser = p.chromium.launch(headless=True, channel='chromium-headless-shell')
    print('✅ chromium-headless-shell funcionando')
except:
    browser = p.chromium.launch(headless=True)
    print('✅ chromium padrão funcionando')
browser.close()
"

# 3. Instalar dependências Node.js
echo "Instalando dependências Node.js..."
npm install

# 4. Build do CSS
echo "Compilando CSS..."
npx tailwindcss -i static/src/app.css -o static/build/app.css

# 5. Coletar arquivos estáticos
echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

# 6. Executar migrações
echo "Executando migrações..."
python manage.py migrate

echo "=== BUILD CONCLUÍDO ==="
echo "Para iniciar o servidor: python manage.py runserver"