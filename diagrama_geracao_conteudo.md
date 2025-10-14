# 📊 Diagrama do Processo de Geração de Conteúdo - RadarBR

## 🔄 Fluxo Principal de Publicação

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           🚀 COMANDO DE PUBLICAÇÃO                              │
│                    publish_topic_simple "tema" --words 700                      │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           1️⃣ BUSCA DE NOTÍCIAS RSS                             │
│                                                                                 │
│  • Acessa Google News RSS para o tema                                          │
│  • Obtém lista de itens RSS (últimas notícias)                                │
│  • Seleciona primeiro item da lista                                            │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        2️⃣ RESOLUÇÃO DE URL COM NAVEGADOR                       │
│                                                                                 │
│  🧭 NAVEGADOR HEADLESS (Playwright):                                           │
│  • Abre link do Google News                                                    │
│  • Segue redirects automaticamente                                             │
│  • Clica em banners de consentimento                                           │
│  • Aguarda carregamento completo (60s timeout)                                 │
│  • Extrai URL final do site original                                           │
│                                                                                 │
│  🔄 SE FALHAR:                                                                  │
│  • Tenta próximo item da lista RSS                                             │
│  • Máximo 3 tentativas                                                         │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          3️⃣ EXTRAÇÃO DE CONTEÚDO                               │
│                                                                                 │
│  📰 DADOS EXTRAÍDOS:                                                           │
│  • Título da notícia                                                           │
│  • Descrição/resumo                                                            │
│  • Data de publicação                                                          │
│  • Fonte/portal                                                                │
│  • Conteúdo completo do artigo                                                 │
│  • Categoria (se disponível no site)                                          │
│  • Imagens (se disponíveis)                                                    │
│                                                                                 │
│  📊 CONTAGEM DE PALAVRAS:                                                      │
│  • Conta palavras do artigo completo                                           │
│  • Calcula margem de 15% (±)                                                  │
│  • Define target mínimo e máximo                                               │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           4️⃣ GERAÇÃO DE TÍTULO                                │
│                                                                                 │
│  🎯 REGRAS DE TÍTULO:                                                          │
│  • Baseado no título original                                                  │
│  • Remove nomes de portais (G1, UOL, etc.)                                    │
│  • Substitui colunistas por termos genéricos                                  │
│  • Usa variações para evitar repetição                                         │
│  • Máximo 120 caracteres                                                      │
│  • SEO otimizado                                                               │
│                                                                                 │
│  📝 EXEMPLOS DE VARIAÇÕES:                                                     │
│  • "Entenda o caso:"                                                           │
│  • "Análise completa:"                                                         │
│  • "Tudo sobre:"                                                               │
│  • "Detalhes importantes:"                                                    │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        5️⃣ GERAÇÃO DE CONTEÚDO COM IA                           │
│                                                                                 │
│  🤖 OPENAI GPT-4O-MINI:                                                         │
│  • Prompt detalhado com contexto da notícia                                   │
│  • Instruções para reescrita completa                                          │
│  • Linguagem humanizada e brasileira                                          │
│  • Estrutura: 2 seções H2                                                     │
│  • Margem de palavras específica                                               │
│  • max_tokens: 4000                                                            │
│                                                                                 │
│  🔄 PROCESSO DE VALIDAÇÃO:                                                     │
│  • Conta palavras do conteúdo gerado                                           │
│  • Verifica se está dentro da margem (85% do mínimo)                          │
│  • Se falhar: tenta segunda vez                                                │
│  • Se ambas falharem: cancela publicação                                       │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           6️⃣ DETERMINAÇÃO DE CATEGORIA                         │
│                                                                                 │
│  📂 HIERARQUIA DE CATEGORIZAÇÃO:                                               │
│                                                                                 │
│  1️⃣ CATEGORIA DO PUBLISHER:                                                    │
│     • Extraída diretamente do site original                                    │
│     • Usa CSS selectors específicos                                           │
│                                                                                 │
│  2️⃣ INFERÊNCIA POR URL:                                                       │
│     • Analisa palavras-chave na URL                                            │
│     • Mapeia para categorias conhecidas                                        │
│                                                                                 │
│  3️⃣ CATEGORIZADOR INTELIGENTE:                                                 │
│     • Analisa conteúdo gerado                                                  │
│     • Usa palavras-chave semânticas                                            │
│     • Densidade de termos por categoria                                        │
│     • Regras especiais para notícias internacionais                            │
│                                                                                 │
│  4️⃣ FALLBACK:                                                                  │
│     • "Brasil" ou primeira categoria disponível                                │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           7️⃣ BUSCA DE IMAGENS                                 │
│                                                                                 │
│  🖼️ HIERARQUIA DE IMAGENS:                                                     │
│                                                                                 │
│  1️⃣ IMAGENS DO ARTIGO ORIGINAL:                                                │
│     • Extraídas do site original                                               │
│     • URLs diretas para as imagens                                            │
│                                                                                 │
│  2️⃣ UNSPLASH API:                                                             │
│     • Busca por termos relacionados ao tema                                   │
│     • Timeout: 20 segundos                                                     │
│     • URLs de alta qualidade                                                   │
│                                                                                 │
│  3️⃣ PEXELS API (FALLBACK):                                                    │
│     • Se Unsplash falhar                                                       │
│     • Mesma estratégia de busca                                                │
│                                                                                 │
│  4️⃣ IMAGEM LOCAL (ÚLTIMO RECURSO):                                            │
│     • Imagem padrão por categoria                                              │
│     • Garante que sempre há uma imagem                                         │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          8️⃣ ESTRUTURAÇÃO SEO                                   │
│                                                                                 │
│  🔧 OTIMIZAÇÕES SEO:                                                           │
│                                                                                 │
│  📝 SLUG:                                                                       │
│  • Normalizado para ASCII                                                      │
│  • Hífens em vez de espaços                                                    │
│  • Timestamp para unicidade                                                     │
│                                                                                 │
│  📄 META DESCRIPTION:                                                          │
│  • Gerada dos highlights do artigo                                             │
│  • Máximo 160 caracteres                                                       │
│  • Otimizada para SEO                                                          │
│                                                                                 │
│  🏷️ SCHEMA.ORG MARKUP:                                                         │
│  • Article JSON-LD                                                             │
│  • Breadcrumbs JSON-LD                                                         │
│  • Dados estruturados para Google                                              │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        9️⃣ ESTRUTURAÇÃO DE CONTEÚDO                            │
│                                                                                 │
│  📋 DIVISÃO EM SEÇÕES:                                                         │
│                                                                                 │
│  • Conteúdo dividido em 2 seções H2                                            │
│  • Banner AdSense inserido entre as seções                                     │
│  • Filtro Django: split_content_sections                                       │
│                                                                                 │
│  🎯 ESTRATÉGIA SEO:                                                            │
│  • Banner posicionado estrategicamente                                         │
│  • Conteúdo bem distribuído                                                    │
│  • Estrutura clara para leitores e bots                                        │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            🔟 SALVAMENTO NO BANCO                              │
│                                                                                 │
│  💾 MODELO NOTICIA:                                                             │
│  • Título gerado                                                                │
│  • Conteúdo HTML estruturado                                                   │
│  • Slug único                                                                   │
│  • Categoria determinada                                                       │
│  • URL da fonte original                                                        │
│  • URL da imagem                                                                │
│  • Data de publicação                                                           │
│  • Status: publicado                                                            │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              ✅ PUBLICAÇÃO CONCLUÍDA                           │
│                                                                                 │
│  🎉 RESULTADO FINAL:                                                            │
│  • Artigo único e original                                                     │
│  • SEO otimizado                                                                │
│  • Estrutura profissional                                                      │
│  • Imagem relevante                                                            │
│  • Categoria correta                                                           │
│  • Disponível no site                                                          │
└─────────────────────────────────────────────────────────────────────────────────┘

## 🔧 Componentes Técnicos Principais

### 📁 Arquivos Principais:
- `rb_ingestor/management/commands/publish_topic_simple.py` - Comando principal
- `rb_ingestor/news_content_extractor.py` - Extrator de conteúdo
- `rb_ingestor/smart_categorizer.py` - Categorizador inteligente
- `rb_portal/templatetags/rb_filters.py` - Filtros de template
- `rb_portal/templates/rb_portal/post_detail.html` - Template do artigo

### 🛠️ Tecnologias Utilizadas:
- **Django** - Framework web
- **Playwright** - Navegador headless
- **OpenAI GPT-4o-mini** - Geração de conteúdo
- **BeautifulSoup** - Parsing HTML
- **Unsplash/Pexels APIs** - Busca de imagens
- **SQLite** - Banco de dados

### ⚙️ Configurações Importantes:
- **Margem de palavras:** 15% (±)
- **Timeout navegador:** 60 segundos
- **Max tokens OpenAI:** 4000
- **Tentativas IA:** 2 máximo
- **Timeout Unsplash:** 20 segundos

## 🚨 Pontos de Falha e Recuperação

### ❌ Falhas Possíveis:
1. **RSS indisponível** → Tenta próximo item
2. **URL não resolve** → Tenta próximo item  
3. **Conteúdo não extrai** → Tenta próximo item
4. **IA falha 2x** → Cancela publicação
5. **Imagem não encontra** → Usa fallback local

### ✅ Estratégias de Recuperação:
- **Múltiplas tentativas** em cada etapa
- **Fallbacks inteligentes** para imagens
- **Validação flexível** para conteúdo
- **Logs detalhados** para debug
- **Cancelamento limpo** se necessário
