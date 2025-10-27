# 🤖 Automação de Postagem no Facebook

Este documento explica como configurar a postagem automática de notícias no Facebook.

## 📋 Requisitos

1. **Facebook SDK**: Já adicionado ao `requirements.txt`
2. **Page Access Token**: Token de acesso da sua página do Facebook
3. **Page ID**: ID da sua página (já temos: `61582919670990`)

## 🔧 Como Obter o Page Access Token

### Passo 1: Acessar o Facebook Developers

1. Acesse: https://developers.facebook.com/
2. Faça login com sua conta do Facebook

### Passo 2: Criar um App

1. Clique em **"Meus Apps"** → **"Criar App"**
2. Escolha o tipo: **"Publicador de Conteúdo"**
3. Preencha:
   - **Nome**: RadarBR
   - **Email de contato**: seu email
4. Clique em **"Criar App ID"**

### Passo 3: Configurar Permissões

1. No painel do app, vá em **"Ferramentas"** → **"Graph API Explorer"**
2. Na seção **"Permission"**, adicione:
   - `pages_manage_posts` (Publicar posts na página)
   - `pages_read_engagement` (Ler engajamento)
   - `pages_show_list` (Listar páginas)

### Passo 4: Obter o Access Token Curto

1. No **Graph API Explorer**:
   - Selecione seu app
   - Em **"Permissões"**, marque: `pages_manage_posts`, `pages_read_engagement`
   - Em **"Token de Acesso de Usuário"**, clique em **"Gerar Token de Acesso"**
2. Copie o token (é temporário, dura 1 hora)

### Passo 5: Converter em Page Access Token Permanente

1. Abra esta URL (substitua `SEU_TOKEN` pelo token do passo anterior):
```
https://graph.facebook.com/v18.0/me/accounts?access_token=SEU_TOKEN
```

2. Você verá uma lista com suas páginas. Encontre a página **RadarBR** e copie o token do campo **"access_token"**

### Passo 6: Tornar o Token Permanente (Opcional)

1. Abra esta URL (substitua `SEU_PAGE_TOKEN` pelo token da etapa anterior):
```
https://graph.facebook.com/v18.0/me?fields=access_token&access_token=SEU_PAGE_TOKEN
```

2. Copie o token gerado

### Passo 7: Configurar no Ambiente

Adicione as variáveis de ambiente no seu servidor:

```bash
export FACEBOOK_PAGE_ACCESS_TOKEN="seu_token_aqui"
export FACEBOOK_PAGE_ID="61582919670990"
export SITE_BASE_URL="https://radarbr.com.br"
```

Ou configure no arquivo `.env`:

```env
FACEBOOK_PAGE_ACCESS_TOKEN=seu_token_aqui
FACEBOOK_PAGE_ID=61582919670990
SITE_BASE_URL=https://radarbr.com.br
```

## 🚀 Como Funciona

1. **Signal**: Quando uma notícia é publicada no Django Admin ou via comando, um signal detecta automaticamente
2. **FacebookPublisher**: A classe `FacebookPublisher` formata a mensagem e publica no Facebook
3. **Conteúdo**: O post inclui:
   - Emoji 📰
   - Título da notícia
   - Resumo (primeiros 200 caracteres)
   - Link para leitura completa
   - Categoria da notícia (hashtag)
   - Imagem da notícia (se disponível)

## 📝 Exemplo de Post

```
📰 Nova Lei de Segurança Pública é aprovada

A nova legislação visa modernizar o sistema de segurança pública do país...

👉 Leia mais: https://radarbr.com.br/noticia/nova-lei-seguranca-publica/

#Política
```

## 🔍 Testando

Para testar se funciona, publique uma notícia pelo Django Admin e verifique se aparece no Facebook!

## ⚠️ Importante

- O token expira após alguns dias/semanas. Monitore os logs
- Se os posts não aparecerem, verifique os logs do Django
- Em desenvolvimento local, configure as variáveis de ambiente antes de rodar o servidor

## 📊 Logs

Os logs mostram:
- ✅ Posts publicados com sucesso
- ⚠️ Avisos de configuração
- ❌ Erros de publicação

Verifique os logs em:
```bash
tail -f logs/django.log
```

## 🔄 Desabilitar Automação

Se precisar desabilitar temporariamente, comente o `import` no `apps.py`:

```python
def ready(self):
    # import rb_noticias.signals  # Comentar esta linha
    pass
```

