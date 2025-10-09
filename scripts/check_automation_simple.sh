#!/bin/bash
# Script simplificado para executar automação no Render

echo "=== VERIFICAÇÃO DE AUTOMAÇÃO RENDER ==="

# Mudar para o diretório do projeto
cd /opt/render/project/src

# Ativar ambiente virtual
source .venv/bin/activate

# Verificar notícias recentes
echo "Verificando notícias recentes..."
python manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from rb_noticias.models import Noticia

total = Noticia.objects.count()
recentes = Noticia.objects.filter(
    criado_em__gte=timezone.now() - timedelta(hours=24)
).count()

print(f'Total notícias: {total}')
print(f'Últimas 24h: {recentes}')

if recentes < 3:
    print('⚠️ Poucas notícias recentes - executando automação...')
    exit(1)  # Sinalizar que precisa executar automação
else:
    print('✅ Quantidade adequada de notícias recentes.')
    exit(0)
"

# Se o comando anterior retornou 1, executar automação
if [ $? -eq 1 ]; then
    echo "Executando automação..."
    python manage.py manual_publish --count 3 --strategy mixed
    
    if [ $? -eq 0 ]; then
        echo "✅ Automação executada com sucesso!"
    else
        echo "❌ Erro na automação"
        exit 1
    fi
fi

# Mostrar últimas notícias
echo ""
echo "=== ÚLTIMAS 5 NOTÍCIAS ==="
python manage.py shell -c "
from rb_noticias.models import Noticia
for n in Noticia.objects.order_by('-criado_em')[:5]:
    print(f'- {n.titulo} ({n.criado_em.strftime(\"%Y-%m-%d %H:%M\")})')
"

echo ""
echo "=== VERIFICAÇÃO CONCLUÍDA ==="
