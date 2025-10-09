# COMANDOS PARA GERAR NOTÍCIAS NO RENDER

## 🚀 **COMANDOS QUE FUNCIONAM**

### **1. Comando Ultra-Simples (Recomendado)**
```bash
python manage.py noticias_simples --num 3
```

### **2. Comando Simples com Debug**
```bash
python manage.py gerar_noticias --limit 3 --debug
```

### **3. Script Python Direto**
```bash
python gerar_noticias_render.py
python gerar_noticias_render.py 5
```

### **4. Comando de Diagnóstico**
```bash
python manage.py diagnosticar_problema
```

## ⚠️ **PROBLEMA IDENTIFICADO**

O comando `python manage.py smart_automation --mode auto` está com problemas porque:

1. **Dependências externas**: Requer módulos como `cloudinary_storage` que podem não estar instalados
2. **Lógica complexa**: Muitas dependências podem falhar
3. **Possível bug**: Pode estar criando categorias em vez de notícias devido a erro na lógica

## 🔧 **SOLUÇÕES ALTERNATIVAS**

### **Para uso no Shell do Render:**

**Opção 1 - Mais simples:**
```bash
python manage.py noticias_simples --num 3
```

**Opção 2 - Com mais controle:**
```bash
python manage.py gerar_noticias --limit 3 --debug --force
```

**Opção 3 - Script direto:**
```bash
python gerar_noticias_render.py 3
```

### **Comando em uma linha (Shell):**
```bash
python manage.py shell -c "
from rb_noticias.models import Noticia, Categoria
from django.utils import timezone
from slugify import slugify
import random

cat, _ = Categoria.objects.get_or_create(slug='geral', defaults={'nome': 'Geral'})
topicos = ['Tecnologia', 'Economia', 'Esportes', 'Cultura', 'Política']

for i in range(3):
    topico = random.choice(topicos)
    timestamp = timezone.now().strftime('%d/%m %H:%M')
    titulo = f'{topico} - {timestamp}'
    slug = slugify(titulo)[:180]
    
    if not Noticia.objects.filter(slug=slug).exists():
        Noticia.objects.create(
            titulo=titulo,
            slug=slug,
            conteudo=f'<h2>{topico}</h2><p>Artigo sobre {topico}.</p>',
            publicado_em=timezone.now(),
            categoria=cat,
            fonte_url=f'manual-{timezone.now().strftime(\"%Y%m%d-%H%M\")}-{i}',
            fonte_nome='RadarBR Manual',
            status=1
        )
        print(f'✓ Criado: {titulo}')

print(f'Total: {Noticia.objects.count()}')
"
```

## 📋 **VERIFICAÇÃO**

**Verificar notícias criadas:**
```bash
python manage.py shell -c "
from rb_noticias.models import Noticia
print('Últimas 5 notícias:')
for n in Noticia.objects.order_by('-criado_em')[:5]:
    print(f'- {n.titulo} ({n.categoria.nome if n.categoria else \"Sem categoria\"})')
"
```

## 🎯 **RECOMENDAÇÃO FINAL**

Use o comando mais simples e confiável:
```bash
python manage.py noticias_simples --num 3
```

Este comando:
- ✅ Funciona sem dependências externas
- ✅ Cria notícias reais (não categorias)
- ✅ É simples e confiável
- ✅ Funciona no Render
- ✅ Tem tratamento de erros
