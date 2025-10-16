#!/bin/bash
# Script para instalar Playwright automaticamente no startup (apenas se necessário)

echo "=== VERIFICANDO PLAYWRIGHT ==="

# Garantir que estamos no diretório correto
cd /opt/render/project/src

# Ativar ambiente virtual
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Configurar variáveis de ambiente
export PLAYWRIGHT_BROWSERS_PATH=0

# Verificar se Playwright está instalado
if ! python -c "import playwright" 2>/dev/null; then
    echo "Instalando Playwright..."
    pip install playwright
fi

# Verificar se chromium-headless-shell está disponível
if ! python -c "
from playwright.sync_api import sync_playwright
p = sync_playwright().start()
try:
    browser = p.chromium.launch(headless=True, channel='chromium-headless-shell')
    browser.close()
    print('chromium-headless-shell OK')
except:
    print('chromium-headless-shell FALTANDO')
" 2>/dev/null | grep -q "OK"; then
    echo "✅ chromium-headless-shell já está funcionando"
else
    echo "Instalando chromium-headless-shell..."
    python -m playwright install chromium-headless-shell || echo "⚠ chromium-headless-shell falhou"
fi

# Verificar se chromium padrão está disponível
if ! python -c "
from playwright.sync_api import sync_playwright
p = sync_playwright().start()
try:
    browser = p.chromium.launch(headless=True)
    browser.close()
    print('chromium OK')
except:
    print('chromium FALTANDO')
" 2>/dev/null | grep -q "OK"; then
    echo "✅ chromium já está funcionando"
else
    echo "Instalando chromium..."
    python -m playwright install chromium
fi

echo "=== PLAYWRIGHT VERIFICADO ==="
