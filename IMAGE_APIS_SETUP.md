# IMAGE_APIS_SETUP.md
"""
Configuração das APIs de Imagens Gratuitas

Este documento explica como configurar as APIs gratuitas para busca automática de imagens.
"""

## APIs Suportadas

### 1. Unsplash (Recomendado)
- **URL**: https://unsplash.com/developers
- **Limite**: 50 requests/hora (gratuito)
- **Qualidade**: Excelente
- **Configuração**:
  ```bash
  # Adicionar ao .env
  UNSPLASH_API_KEY=sua_chave_aqui
  ```

### 2. Pexels
- **URL**: https://www.pexels.com/api/
- **Limite**: 200 requests/hora (gratuito)
- **Qualidade**: Muito boa
- **Configuração**:
  ```bash
  # Adicionar ao .env
  PEXELS_API_KEY=sua_chave_aqui
  ```

### 3. Pixabay
- **URL**: https://pixabay.com/api/docs/
- **Limite**: 5.000 requests/hora (gratuito)
- **Qualidade**: Boa
- **Configuração**:
  ```bash
  # Adicionar ao .env
  PIXABAY_API_KEY=sua_chave_aqui
  ```

## Como Obter as Chaves

### Unsplash
1. Acesse https://unsplash.com/developers
2. Clique em "Your apps"
3. Clique em "New Application"
4. Preencha os dados do seu site
5. Copie a "Access Key"

### Pexels
1. Acesse https://www.pexels.com/api/
2. Clique em "Request API Key"
3. Preencha o formulário
4. Confirme o email
5. Copie a chave da API

### Pixabay
1. Acesse https://pixabay.com/api/docs/
2. Clique em "Get API Key"
3. Crie uma conta ou faça login
4. Copie a chave da API

## Configuração Completa

Adicione todas as chaves ao seu arquivo `.env`:

```bash
# APIs de Imagens
UNSPLASH_API_KEY=abc123def456...
PEXELS_API_KEY=xyz789uvw012...
PIXABAY_API_KEY=mno345pqr678...
```

## Uso dos Comandos

### Buscar Imagens para Notícias Existentes
```bash
# Buscar imagens para 10 notícias sem imagem
python manage.py find_images_for_news --limit 10

# Buscar apenas para categoria específica
python manage.py find_images_for_news --category "tecnologia" --limit 5

# Modo dry-run (apenas simular)
python manage.py find_images_for_news --dry-run --limit 20
```

### Gerenciar Cache de Imagens
```bash
# Ver estatísticas do cache
python manage.py manage_image_cache --stats

# Limpar entradas expiradas
python manage.py manage_image_cache --clear-expired

# Validar URLs em cache
python manage.py manage_image_cache --validate

# Listar todas as entradas
python manage.py manage_image_cache --list
```

## Estratégia de Busca

O sistema usa uma estratégia inteligente:

1. **Extração de Palavras-chave**: Analisa título e conteúdo
2. **Priorização**: Palavras do título têm prioridade
3. **Fallback por Categoria**: Se não encontrar imagem específica, busca genérica da categoria
4. **Cache Inteligente**: Evita buscas repetidas
5. **Validação**: Verifica se URLs ainda estão ativas

## Limites e Boas Práticas

- **Respeite os limites**: Cada API tem limites diferentes
- **Cache é essencial**: Evita buscas desnecessárias
- **Validação regular**: URLs podem ficar inativas
- **Fallback inteligente**: Sempre há uma imagem de categoria

## Monitoramento

Use os comandos de gerenciamento para monitorar:
- Taxa de sucesso das buscas
- Performance do cache
- URLs inválidas
- Uso das APIs

## Troubleshooting

### Erro: "Must supply api_key"
- Verifique se as variáveis estão no `.env`
- Reinicie o servidor Django
- Teste com `python manage.py manage_image_cache --stats`

### Erro: "Rate limit exceeded"
- Aguarde o reset do limite (geralmente 1 hora)
- Use cache para reduzir buscas
- Considere upgrade das APIs

### Imagens não aparecem
- Verifique se URLs estão válidas
- Execute validação: `--validate`
- Verifique logs do Django
