#!/bin/bash
# Script de teste para Render
# Verifica se o Django está funcionando

set -e

echo "=== TESTE RENDER DJANGO ==="
echo "Data/Hora: $(date)"
echo "Diretório: $(pwd)"
echo "Python: $(which python)"
echo "Django: $(python -c 'import django; print(django.get_version())')"

# Testar comando Django
echo "Testando comando Django..."
python manage.py test_render

echo "=== TESTE CONCLUÍDO ==="
