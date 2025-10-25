# 📋 CRITÉRIO PARA NOTÍCIAS NA SEÇÃO "EM ALTA"

## 🔍 **Critério Atual:**

### **✅ Lógica da Sidebar:**
```html
{% with hot=trending|default:others|default:page_obj.object_list %}
  {% for obj in hot|slice:':4' %}
```

**Prioridade de Exibição:**
1. **`trending`** (se existir)
2. **`others`** (se trending não existir)
3. **`page_obj.object_list`** (se os anteriores não existirem)

### **✅ Como `others` é Definido:**

#### **Na View `home()`:**
```python
# Buscar outras notícias (excluindo a featured) - sempre as mais recentes
others_qs = all_news.exclude(id=featured.id) if featured else all_news
others = list(others_qs[:3])  # As 3 mais recentes após a featured
```

#### **Nas Outras Views:**
```python
qs = Noticia.objects.filter(status=Noticia.Status.PUBLICADO).order_by("-publicado_em")
others = list(qs[1:3])  # Para a sidebar
```

## 🎯 **Critério Atual:**

### **✅ 1. Status da Notícia:**
- **Apenas publicadas**: `status=Noticia.Status.PUBLICADO`
- **Rascunhos excluídos**: Não aparecem na sidebar

### **✅ 2. Ordem Cronológica:**
- **Mais recente primeiro**: `order_by("-publicado_em")`
- **Data de publicação**: Critério principal de ordenação

### **✅ 3. Exclusão de Destaque:**
- **Na home**: Exclui a notícia em destaque (`exclude(id=featured.id)`)
- **Outras páginas**: Pula a primeira notícia (`qs[1:3]`)

### **✅ 4. Limite de Exibição:**
- **Máximo 4 notícias**: `slice:':4'`
- **Template**: Mostra até 4 itens na sidebar

## 📊 **Exemplos Práticos:**

### **✅ Cenário 1: Home Page**
```
Notícia A (destaque) - Publicada hoje
Notícia B (recente)  - Publicada hoje
Notícia C (recente)  - Publicada ontem
Notícia D (recente)  - Publicada há 2 dias
```

**Resultado "Em alta":**
- Notícias B, C, D (excluindo A que está em destaque)

### **✅ Cenário 2: Página de Categoria**
```
Notícia A (recente)  - Publicada hoje
Notícia B (recente)  - Publicada ontem
Notícia C (recente)  - Publicada há 2 dias
Notícia D (recente)  - Publicada há 3 dias
```

**Resultado "Em alta":**
- Notícias B, C, D (pulando A que é a primeira)

## 🤔 **Problemas Identificados:**

### **❌ 1. Critério Simples Demais:**
- **Apenas cronológico**: Não considera engajamento
- **Sem métricas**: Não há views, cliques, comentários
- **Estático**: Não muda baseado em comportamento

### **❌ 2. Exclusão Arbitrária:**
- **Pula primeira**: Sempre exclui a mais recente
- **Sem lógica**: Não há critério claro para exclusão
- **Inconsistente**: Diferente comportamento entre páginas

### **❌ 3. Falta de Personalização:**
- **Sem trending real**: Não há algoritmo de tendências
- **Sem categorização**: Não considera categoria da página
- **Sem relevância**: Não há sistema de relevância

## 💡 **Sugestões de Melhoria:**

### **✅ Opção 1: Sistema de Trending Real**
```python
# Baseado em views, cliques, tempo de leitura
trending = Noticia.objects.filter(
    status=Noticia.Status.PUBLICADO
).annotate(
    trending_score=Count('views') + Count('clicks') * 2
).order_by('-trending_score', '-publicado_em')[:4]
```

### **✅ Opção 2: Notícias Mais Visualizadas**
```python
# Baseado em número de visualizações
trending = Noticia.objects.filter(
    status=Noticia.Status.PUBLICADO
).order_by('-views', '-publicado_em')[:4]
```

### **✅ Opção 3: Notícias por Categoria**
```python
# Baseado na categoria da página atual
if categoria_atual:
    trending = Noticia.objects.filter(
        status=Noticia.Status.PUBLICADO,
        categoria=categoria_atual
    ).order_by('-publicado_em')[:4]
```

### **✅ Opção 4: Híbrido (Recomendado)**
```python
# Combina recência + engajamento
trending = Noticia.objects.filter(
    status=Noticia.Status.PUBLICADO
).annotate(
    score=F('views') + F('clicks') * 2 + F('publicado_em__day') * 0.1
).order_by('-score')[:4]
```

## 🎯 **Qual Critério Você Prefere?**

**A**: Manter atual (apenas cronológico)
**B**: Implementar sistema de trending real
**C**: Baseado em visualizações
**D**: Por categoria da página
**E**: Sistema híbrido (recência + engajamento)

Qual dessas opções faz mais sentido para o seu site?
