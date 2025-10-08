# Comandos para Sincronizar Render com Local

## 🚀 Script Principal
```bash
# No shell do Render
python scripts/sync_render.py
```

## 📋 Comandos Individuais

### 1. Verificar Ambiente
```bash
python manage.py shell -c "
from django.conf import settings
print(f'DEBUG: {settings.DEBUG}')
print(f'ADSENSE_CLIENT: {getattr(settings, \"ADSENSE_CLIENT\", \"Não configurado\")}')
print(f'GA4_ID: {getattr(settings, \"GA4_ID\", \"Não configurado\")}')
"
```

### 2. Verificar Notícias
```bash
python manage.py shell -c "
from rb_noticias.models import Noticia
from django.utils import timezone
from datetime import timedelta

total = Noticia.objects.count()
recentes = Noticia.objects.filter(
    criado_em__gte=timezone.now() - timedelta(hours=24)
).count()

print(f'Total: {total}')
print(f'Últimas 24h: {recentes}')

if recentes < 3:
    print('⚠️ Executando automação...')
    from django.core.management import call_command
    call_command('auto_publish', '--quick')
    print('✅ Automação executada')
"
```

### 3. Executar Automação
```bash
# Automação rápida
python manage.py auto_publish --quick

# Automação completa
python manage.py run_scheduler --force

# Publicação específica
python manage.py smart_trends_publish --strategy mixed --limit 3 --force
```

### 4. Limpar e Atualizar
```bash
# Limpar cache
python manage.py shell -c "
from django.core.cache import cache
cache.clear()
print('Cache limpo')
"

# Atualizar sitemap
python manage.py ping_sitemap
```

### 5. Verificar Resultado
```bash
python manage.py shell -c "
from rb_noticias.models import Noticia
print('Últimas 5 notícias:')
for n in Noticia.objects.order_by('-criado_em')[:5]:
    print(f'- {n.titulo} ({n.publicado_em})')
"
```

## 🔧 Comando Completo em Uma Linha
```bash
python manage.py shell -c "
from rb_noticias.models import Noticia
from django.utils import timezone
from datetime import timedelta
from django.core.management import call_command
from django.core.cache import cache

print('=== SINCRONIZAÇÃO RENDER ===')
total = Noticia.objects.count()
recentes = Noticia.objects.filter(criado_em__gte=timezone.now() - timedelta(hours=24)).count()
print(f'Total: {total}, Últimas 24h: {recentes}')

if recentes < 3:
    print('Executando automação...')
    call_command('auto_publish', '--quick')
    print('Automação executada')

cache.clear()
call_command('ping_sitemap')
print('Cache limpo e sitemap atualizado')
print('Últimas 3:')
for n in Noticia.objects.order_by('-criado_em')[:3]:
    print(f'- {n.titulo}')
"
```

## 📅 Agendamento Automático
```bash
# Adicionar ao crontab do Render (executar a cada 6 horas)
0 */6 * * * cd /opt/render/project/src && source .venv/bin/activate && python scripts/sync_render.py >> /opt/render/project/logs/sync.log 2>&1
```

## 🎯 Objetivos do Script
- ✅ Verificar configurações do ambiente
- ✅ Contar notícias existentes
- ✅ Executar automação se necessário
- ✅ Limpar cache
- ✅ Atualizar sitemap
- ✅ Mostrar resumo final

## 📊 Monitoramento
```bash
# Ver logs de sincronização
tail -f logs/sync.log

# Verificar status
python manage.py test_adsense
```
