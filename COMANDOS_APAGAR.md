# COMANDOS PARA APAGAR NOTÍCIAS NO RENDER

## 🗑️ **COMANDOS PARA APAGAR NOTÍCIAS**

### **1. Comando Django (Recomendado)**
```bash
python manage.py apagar_noticias --num 5
```

### **2. Comando com Confirmação Automática**
```bash
python manage.py apagar_noticias --num 5 --confirm
```

### **3. Comando com Debug**
```bash
python manage.py apagar_noticias --num 5 --debug --confirm
```

### **4. Script Python Direto**
```bash
python apagar_noticias_render.py apagar 5
python apagar_noticias_render.py apagar 5 --confirm
```

### **5. Listar Antes de Apagar**
```bash
python apagar_noticias_render.py listar 10
```

## ⚡ **COMANDO EM UMA LINHA (Shell)**

### **Apagar as últimas 5 notícias:**
```bash
python manage.py shell -c "
from rb_noticias.models import Noticia
ultimas = Noticia.objects.order_by('-criado_em')[:5]
print('Apagando as últimas 5 notícias:')
for n in ultimas:
    print(f'- {n.titulo}')
    n.delete()
print(f'Total restante: {Noticia.objects.count()}')
"
```

### **Apagar apenas 1 notícia (a mais recente):**
```bash
python manage.py shell -c "
from rb_noticias.models import Noticia
ultima = Noticia.objects.order_by('-criado_em').first()
if ultima:
    print(f'Apagando: {ultima.titulo}')
    ultima.delete()
    print(f'Total restante: {Noticia.objects.count()}')
else:
    print('Nenhuma notícia encontrada')
"
```

### **Listar últimas 5 antes de apagar:**
```bash
python manage.py shell -c "
from rb_noticias.models import Noticia
print('Últimas 5 notícias:')
for i, n in enumerate(Noticia.objects.order_by('-criado_em')[:5], 1):
    print(f'{i}. {n.titulo}')
"
```

## 🔍 **VERIFICAÇÃO**

### **Verificar quantas notícias existem:**
```bash
python manage.py shell -c "
from rb_noticias.models import Noticia
print(f'Total de notícias: {Noticia.objects.count()}')
"
```

### **Verificar as últimas notícias:**
```bash
python manage.py shell -c "
from rb_noticias.models import Noticia
print('Últimas 3 notícias:')
for n in Noticia.objects.order_by('-criado_em')[:3]:
    print(f'- {n.titulo} ({n.criado_em})')
"
```

## ⚠️ **CUIDADOS**

1. **Sempre verifique antes de apagar** - use o comando de listar primeiro
2. **Use --confirm apenas quando tiver certeza** - evita confirmação manual
3. **As notícias apagadas não podem ser recuperadas** - operação irreversível
4. **Teste primeiro com poucas notícias** - comece com --num 1

## 🎯 **RECOMENDAÇÃO**

Para uso seguro no Render:
```bash
# 1. Primeiro, listar as notícias
python manage.py shell -c "from rb_noticias.models import Noticia; [print(f'{i}. {n.titulo}') for i, n in enumerate(Noticia.objects.order_by('-criado_em')[:5], 1)]"

# 2. Depois, apagar as desejadas
python manage.py apagar_noticias --num 5
```
