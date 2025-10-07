# 🚀 Configuração do Google AdSense para RadarBR

## ✅ **Slots de Anúncios Implementados:**

### **Sidebar (300px de largura):**
- **Top Banner**: 300x250 (logo após header)
- **Middle Banner**: 300x250 (entre trending e categorias)  
- **Bottom Banner**: 300x600 (skyscraper no final)

### **Conteúdo Principal:**
- **Inline Banner**: 728x90 (após hero, antes da lista)
- **Between Cards**: 728x90 (a cada 4 notícias)

## 🔧 **Implementação:**

### 1. **Adicione o código do AdSense no `base.html`:**
```html
<!-- No <head>, após as meta tags -->
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-SEU_PUBLISHER_ID" crossorigin="anonymous"></script>
```

### 2. **Substitua os placeholders pelos códigos reais:**

**Sidebar Top (300x250):**
```html
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-SEU_PUBLISHER_ID"
     data-ad-slot="SIDE_TOP_SLOT_ID"
     data-ad-format="auto"></ins>
<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
```

**Sidebar Middle (300x250):**
```html
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-SEU_PUBLISHER_ID"
     data-ad-slot="SIDE_MIDDLE_SLOT_ID"
     data-ad-format="auto"></ins>
<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
```

**Sidebar Bottom (300x600):**
```html
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-SEU_PUBLISHER_ID"
     data-ad-slot="SIDE_BOTTOM_SLOT_ID"
     data-ad-format="auto"></ins>
<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
```

**Content Inline (728x90):**
```html
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-SEU_PUBLISHER_ID"
     data-ad-slot="CONTENT_INLINE_SLOT_ID"
     data-ad-format="auto"></ins>
<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
```

**Between Cards (728x90):**
```html
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-SEU_PUBLISHER_ID"
     data-ad-slot="CONTENT_BETWEEN_SLOT_ID"
     data-ad-format="auto"></ins>
<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
```

## 📊 **Estratégia de Monetização:**

### **Posicionamento Otimizado:**
- **Above the fold**: Banner inline após hero
- **Sidebar estratégica**: 3 slots bem distribuídos
- **Content integration**: Entre cards para não interromper leitura
- **Mobile responsive**: Slots se adaptam automaticamente

### **Densidade de Anúncios:**
- **Desktop**: 5 slots por página (dentro dos limites do AdSense)
- **Mobile**: Slots se reorganizam automaticamente
- **Balance**: Conteúdo vs. anúncios otimizado

## 🎯 **Benefícios da Implementação:**

### **Performance:**
- **Lazy loading**: Anúncios carregam conforme necessário
- **Responsive**: Adaptação automática a diferentes telas
- **Non-blocking**: Não afetam velocidade do site

### **SEO:**
- **Semântico**: Estrutura HTML adequada
- **Acessível**: ARIA labels e roles corretos
- **Mobile-first**: Otimizado para dispositivos móveis

### **UX:**
- **Não intrusivo**: Integração natural com o design
- **Relevante**: Posicionamento estratégico
- **Responsivo**: Funciona em todos os dispositivos

## ⚠️ **Políticas Importantes:**

### **AdSense Policies:**
- **Conteúdo original**: Evite conteúdo duplicado
- **Tráfego orgânico**: Não compre tráfego
- **Cliques válidos**: Não clique nos próprios anúncios
- **Política de privacidade**: Obrigatória para AdSense

### **GDPR/Privacy:**
- **Cookie consent**: Implemente banner de cookies
- **Privacy policy**: Link obrigatório no footer
- **Data collection**: Transparência sobre dados coletados

## 🔄 **Próximos Passos:**

1. **Aplicar ao Google AdSense** com o site em produção
2. **Configurar slots** no painel do AdSense
3. **Testar anúncios** em ambiente de teste
4. **Monitorar performance** via AdSense Analytics
5. **Otimizar posicionamento** baseado em dados

---

**💡 Dica**: Os placeholders atuais mostram exatamente onde os anúncios aparecerão. Substitua pelos códigos reais quando aprovado pelo AdSense!
