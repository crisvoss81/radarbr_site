# 📝 COMO ADICIONAR CONTATOS E REDES SOCIAIS NO ADMIN

## 🎯 **Passo a Passo:**

### **1. ✅ Acesse o Admin Django**
- URL: `http://localhost:8000/admin/` (ou seu domínio)
- Faça login com suas credenciais

### **2. ✅ Navegue para Configurações**
- No menu lateral, localize **"RB_PORTAL"**
- Clique em **"Configurações do Site"**

### **3. ✅ Edite a Configuração Existente**
- Clique em **"RadarBR"** (ou na configuração existente)
- O formulário abrirá com todos os campos

### **4. ✅ Preencha os Contatos**

#### **Informações Gerais:**
- **Nome do Site**: RadarBR
- **Slogan**: Suas notícias em tempo real

#### **Contato:**
- **Email contato**: seu-email@radarbr.com.br
- **Email redação**: redacao@radarbr.com.br
- **Telefone**: +55 51 99999-9999 (opcional)
- **Endereço**: Rua Exemplo, 123 - Cidade/UF (opcional)

### **5. ✅ Adicione as Redes Sociais**
Clique em **"Redes Sociais"** para expandir e preencha as URLs:

#### **Exemplos de URLs:**
- **Facebook**: `https://www.facebook.com/radarbr`
- **Instagram**: `https://www.instagram.com/radarbr`
- **Twitter/X**: `https://twitter.com/radarbr`
- **YouTube**: `https://www.youtube.com/@radarbr`
- **LinkedIn**: `https://www.linkedin.com/company/radarbr`
- **Telegram**: `https://t.me/radarbr` ou `@radarbr`

### **6. ✅ Salvar**
- Clique em **"Salvar"** (botão no canto superior direito)
- As informações aparecerão nas páginas do site

## 📍 **Onde as Informações Aparecem:**

### **✅ Página de Contato** (`/contato/`):
- Email de contato
- Email da redação
- Telefone
- Endereço

### **✅ Página de Redes Sociais** (`/redes-sociais/`):
- Links das redes sociais configuradas
- Ícones e cards visuais

## 🎨 **Formato de URLs:**

### **Facebook:**
```
https://www.facebook.com/seu-usuario
https://www.facebook.com/seu-grupo
```

### **Instagram:**
```
https://www.instagram.com/seu-usuario/
https://www.instagram.com/seu-usuario/
```

### **Twitter/X:**
```
https://twitter.com/seu-usuario
https://x.com/seu-usuario
```

### **YouTube:**
```
https://www.youtube.com/@seu-canal
https://www.youtube.com/channel/SEU-ID
```

### **LinkedIn:**
```
https://www.linkedin.com/company/sua-empresa
https://www.linkedin.com/in/seu-perfil
```

### **Telegram:**
```
https://t.me/seu-canal
https://t.me/seu-grupo
```

## 📝 **Campos Disponíveis:**

### **Informações Gerais:**
- `nome_site` - Nome do site
- `slogan` - Slogan do site

### **Contato:**
- `email_contato` - Email principal
- `email_redacao` - Email da redação
- `telefone` - Telefone (opcional)
- `endereco` - Endereço físico (opcional)

### **Redes Sociais:**
- `facebook_url` - URL do Facebook
- `twitter_url` - URL do Twitter/X
- `instagram_url` - URL do Instagram
- `youtube_url` - URL do YouTube
- `linkedin_url` - URL do LinkedIn
- `telegram_url` - URL do Telegram

## 🔒 **Segurança:**

### **Validações:**
- **Emails**: Validados automaticamente
- **URLs**: Validados automaticamente
- **Telefone**: Formato livre (máximo 20 caracteres)
- **Endereço**: Texto livre

### **Limites:**
- Apenas **uma configuração** pode existir
- Não é possível **deletar** a configuração
- Não é possível **adicionar** uma segunda configuração

## ✨ **Dica:**
- **Deixe em branco** as redes sociais que não usar
- As redes sociais configuradas aparecerão com seus ícones
- As redes sociais vazias não aparecerão no site
