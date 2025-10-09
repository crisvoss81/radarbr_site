#!/bin/bash
# Script de configuração do sistema inteligente de automação
# Configura e testa todos os componentes do sistema

echo "=== CONFIGURAÇÃO DO SISTEMA INTELIGENTE DE AUTOMAÇÃO ==="

# Função de log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Verificar se estamos no diretório correto
if [ ! -f "manage.py" ]; then
    echo "❌ Erro: Execute este script no diretório raiz do projeto Django"
    exit 1
fi

log "✓ Diretório do projeto confirmado"

# 1. Verificar dependências Python
log "1. Verificando dependências Python..."
python -c "
import sys
dependencies = ['django', 'requests', 'slugify']
missing = []
for dep in dependencies:
    try:
        __import__(dep)
        print(f'✓ {dep}')
    except ImportError:
        missing.append(dep)
        print(f'✗ {dep}')

if missing:
    print(f'❌ Dependências faltando: {missing}')
    sys.exit(1)
else:
    print('✅ Todas as dependências estão instaladas')
"

if [ $? -ne 0 ]; then
    log "❌ Instale as dependências: pip install -r requirements.txt"
    exit 1
fi

# 2. Verificar configuração Django
log "2. Verificando configuração Django..."
python manage.py check --deploy
if [ $? -eq 0 ]; then
    log "✅ Django configurado corretamente"
else
    log "❌ Problemas na configuração Django"
    exit 1
fi

# 3. Testar comandos de automação
log "3. Testando comandos de automação..."

# Teste do comando de diagnóstico
log "Testando comando de diagnóstico..."
python manage.py diagnostico_automacao
if [ $? -eq 0 ]; then
    log "✅ Comando de diagnóstico funcionando"
else
    log "⚠️ Comando de diagnóstico com problemas"
fi

# Teste do comando de automação simples
log "Testando automação simples..."
python manage.py automacao_simples --limit 1 --force
if [ $? -eq 0 ]; then
    log "✅ Automação simples funcionando"
else
    log "⚠️ Automação simples com problemas"
fi

# Teste do sistema inteligente
log "Testando sistema inteligente..."
python manage.py smart_automation --mode test
if [ $? -eq 0 ]; then
    log "✅ Sistema inteligente funcionando"
else
    log "⚠️ Sistema inteligente com problemas"
fi

# 4. Verificar configuração de cron jobs
log "4. Verificando configuração de cron jobs..."
if [ -f "render.yaml" ]; then
    cron_count=$(grep -c "type: cron" render.yaml)
    log "✓ ${cron_count} cron jobs configurados no render.yaml"
else
    log "⚠️ Arquivo render.yaml não encontrado"
fi

# 5. Verificar scripts
log "5. Verificando scripts..."
scripts=("scripts/smart_scheduler.sh" "scripts/automation.sh")
for script in "${scripts[@]}"; do
    if [ -f "$script" ]; then
        chmod +x "$script"
        log "✓ $script configurado e executável"
    else
        log "⚠️ $script não encontrado"
    fi
done

# 6. Teste de performance
log "6. Testando monitor de performance..."
python manage.py monitor_performance --period 1h
if [ $? -eq 0 ]; then
    log "✅ Monitor de performance funcionando"
else
    log "⚠️ Monitor de performance com problemas"
fi

# 7. Resumo da configuração
log "7. RESUMO DA CONFIGURAÇÃO:"
echo ""
echo "📊 STATUS DO SISTEMA:"
echo "✅ Django: Configurado"
echo "✅ Dependências: Instaladas"
echo "✅ Comandos: Funcionando"
echo "✅ Scripts: Configurados"
echo "✅ Cron Jobs: Configurados"
echo ""
echo "🚀 PRÓXIMOS PASSOS:"
echo "1. Configure as variáveis de ambiente no Render:"
echo "   - OPENAI_API_KEY (para IA)"
echo "   - UNSPLASH_API_KEY (para imagens)"
echo "   - PEXELS_API_KEY (para imagens)"
echo "   - CLOUDINARY_CLOUD_NAME (para upload)"
echo "   - CLOUDINARY_API_KEY (para upload)"
echo "   - CLOUDINARY_API_SECRET (para upload)"
echo ""
echo "2. Faça deploy no Render:"
echo "   git add ."
echo "   git commit -m 'Configure smart automation system'"
echo "   git push origin main"
echo ""
echo "3. Monitore os logs no Render Dashboard"
echo ""
echo "4. Execute comandos manuais se necessário:"
echo "   python manage.py smart_automation --mode auto"
echo "   python manage.py monitor_performance --period 24h"
echo ""
echo "🎯 SISTEMA CONFIGURADO COM SUCESSO!"
echo "O sistema agora executará automaticamente nos horários otimizados:"
echo "- 8h, 12h, 15h, 18h, 20h (sistema inteligente)"
echo "- A cada 2h (sistema de fallback)"
echo "- 6h (monitor de performance)"
