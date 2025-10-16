#!/bin/bash
# deploy-automacao.sh
# Script para executar automação no Render

echo "🚀 Iniciando automação RadarBR..."
cd /opt/render/project/src

# Executar automação
python manage.py automacao_render --limit 3 --force

echo "✅ Automação concluída!"
