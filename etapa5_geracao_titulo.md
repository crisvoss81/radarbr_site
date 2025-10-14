# 📝 Etapa 5 - Geração de Título - Detalhamento Completo

## 🎯 Objetivo
Gerar um título único, SEO-otimizado e humanizado baseado no título original da notícia, evitando plágio e mencionando portais ou colunistas.

## 📊 Fluxo Detalhado da Geração de Título

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           📰 TÍTULO ORIGINAL                                    │
│                    Ex: "Grávida, garota de programa ligada a Neymar surge com    │
│                         exame de DNA - Metrópoles"                              │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        1️⃣ LIMPEZA DE PORTALS                                   │
│                                                                                 │
│  🗑️ PORTALS REMOVIDOS:                                                         │
│  • G1, Globo, Folha, Estadão, UOL, Terra, R7, IG, Exame                       │
│  • Metrópoles, CNN, BBC, Agência Brasil, InfoMoney, GZH                        │
│  • CidadeVerde.com, Midiamax, CLAUDIA, O Globo, Rádio Itatiaia                │
│  • Band, Jornal Correio, TV Cultura                                            │
│                                                                                 │
│  🔧 PADRÕES DE REMOÇÃO:                                                        │
│  • " - Portal" → removido                                                      │
│  • " | Portal" → removido                                                      │
│  • " (Portal)" → removido                                                      │
│                                                                                 │
│  ✅ RESULTADO:                                                                  │
│  "Grávida, garota de programa ligada a Neymar surge com exame de DNA"          │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     2️⃣ REMOÇÃO DE PREFIXOS DE SEÇÃO                            │
│                                                                                 │
│  🗑️ PREFIXOS REMOVIDOS:                                                        │
│  • "Opinião: " → removido                                                      │
│  • "Coluna: " → removido                                                       │
│  • "Análise: " → removido                                                      │
│  • "Blog: " → removido                                                         │
│                                                                                 │
│  🔧 REGEX UTILIZADAS:                                                          │
│  • (?i)^opini[aã]o\s*[-:]+\s*                                                 │
│  • (?i)^coluna\s*[-:]+\s*                                                      │
│  • (?i)^an[áa]lise\s*[-:]+\s*                                                  │
│  • (?i)^blog\s*[-:]+\s*                                                        │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                       3️⃣ SUBSTITUIÇÃO DE COLUNISTAS                            │
│                                                                                 │
│  👤 PADRÕES DE COLUNISTAS:                                                     │
│  • "por João Silva" → "por especialistas"                                       │
│  • "Maria Santos:" → "Especialistas:"                                          │
│  • "Carlos Oliveira:" → "Especialistas:"                                       │
│                                                                                 │
│  🔧 REGEX UTILIZADAS:                                                           │
│  • \bpor\s+[A-ZÁÂÃÉÊÍÓÔÕÚÜÇ][^\-|:]+ → "por especialistas"                    │
│  • ^(?:[A-ZÁÂÃÉÊÍÓÔÕÚÜÇ][a-záâãéêíóôõúüç]+\s+){1,3}: → "Especialistas:"       │
│                                                                                 │
│  ✅ RESULTADO:                                                                  │
│  "Grávida, garota de programa ligada a Neymar surge com exame de DNA"          │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        4️⃣ NORMALIZAÇÃO FINAL                                   │
│                                                                                 │
│  🧹 LIMPEZA APLICADA:                                                           │
│  • Múltiplos espaços → espaço único                                            │
│  • Pontuação final desnecessária → removida                                    │
│  • ":" ou "-" no final → removidos                                             │
│                                                                                 │
│  🔧 REGEX UTILIZADAS:                                                           │
│  • \s+ → " " (espaço único)                                                    │
│  • [:\-—]\s*$ → "" (remove pontuação final)                                    │
│                                                                                 │
│  ✅ RESULTADO LIMPO:                                                            │
│  "Grávida, garota de programa ligada a Neymar surge com exame de DNA"          │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        5️⃣ GERAÇÃO DE VARIAÇÕES                                │
│                                                                                 │
│  🎲 VARIAÇÕES DISPONÍVEIS:                                                     │
│                                                                                 │
│  1️⃣ "O que muda com {base}"                                                    │
│  2️⃣ "{base} — contexto e impactos"                                            │
│  3️⃣ "{base}: pontos-chave e próximos passos"                                  │
│  4️⃣ "{base} | o que aconteceu e o que vem aí"                                  │
│  5️⃣ "Análise: {base}"                                                         │
│  6️⃣ "Resumo e próximos passos: {base}"                                       │
│  7️⃣ "{base}: entenda em detalhes"                                             │
│  8️⃣ "{base}: análise completa"                                                │
│  9️⃣ "{base}: o que você precisa saber"                                         │
│  🔟 "{base}: fatos e perspectivas"                                             │
│                                                                                 │
│  🚫 CONDIÇÃO ESPECIAL:                                                         │
│  • "Entenda o caso: {base}" → só se não estiver já no título                  │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        6️⃣ SELEÇÃO PSEUDO-DETERMINÍSTICA                       │
│                                                                                 │
│  🎯 ALGORITMO DE SELEÇÃO:                                                       │
│                                                                                 │
│  1️⃣ CALCULAR HASH:                                                             │
│     • hash(título_base) → número único                                         │
│     • abs(hash) % len(variações) → índice                                      │
│                                                                                 │
│  2️⃣ TENTAR VARIAÇÕES:                                                         │
│     • Começar pelo índice calculado                                            │
│     • Verificar limite de 120 caracteres                                      │
│     • Se exceder, tentar próxima variação                                     │
│                                                                                 │
│  3️⃣ FALLBACK:                                                                 │
│     • Se nenhuma variação couber → truncar primeira em 120 chars               │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            ✅ TÍTULO FINAL                                     │
│                                                                                 │
│  📝 EXEMPLO DE RESULTADO:                                                       │
│                                                                                 │
│  Título Original:                                                               │
│  "Grávida, garota de programa ligada a Neymar surge com exame de DNA - Metrópoles" │
│                                                                                 │
│  Título Gerado:                                                                 │
│  "Grávida, garota de programa ligada a Neymar surge com exame de DNA: entenda em detalhes" │
│                                                                                 │
│  🎯 CARACTERÍSTICAS:                                                            │
│  • ✅ Portal removido (Metrópoles)                                             │
│  • ✅ SEO otimizado                                                            │
│  • ✅ Único e não plagiado                                                     │
│  • ✅ Máximo 120 caracteres                                                    │
│  • ✅ Linguagem natural                                                        │
└─────────────────────────────────────────────────────────────────────────────────┘

## 🔧 Configurações Técnicas

### 📊 Limites e Validações:
- **Máximo de caracteres:** 120
- **Hash determinístico:** Para evitar repetição
- **Fallback:** Se nenhuma variação couber

### 🎯 Estratégias Anti-Plágio:
- **Remoção de portais** conhecidos
- **Substituição de colunistas** por termos genéricos
- **Variações de estrutura** (prefixos, sufixos, pontuação)
- **Seleção pseudo-aleatória** baseada em hash

### 📈 Otimizações SEO:
- **Palavras-chave preservadas** do título original
- **Estrutura clara** e legível
- **Pontuação variada** (:, |, —)
- **Call-to-action** implícito ("entenda", "análise")

## 🚨 Casos Especiais

### ❌ Título Original Inválido:
- **Fallback:** "Análise completa: {topic.title()}"
- **Exemplo:** "Análise completa: Asteroide"

### 🔄 Evitar Repetição:
- **Hash do título base** garante variação
- **Verificação de prefixos** existentes
- **Rotação automática** entre variações

### 📏 Limite de Caracteres:
- **Prioridade:** Primeira variação que couber
- **Truncamento:** Se necessário, corta em 120 chars
- **Preservação:** Sempre mantém palavras-chave principais

## 📊 Exemplos Práticos

### 🔄 Transformações Comuns:

| Original | Limpo | Final |
|----------|-------|-------|
| "Lula anuncia medidas - G1" | "Lula anuncia medidas" | "Lula anuncia medidas: entenda em detalhes" |
| "Opinião: Economia em crise por João Silva" | "Economia em crise por especialistas" | "Economia em crise por especialistas: análise completa" |
| "Bolsonaro: declarações polêmicas | UOL" | "Bolsonaro: declarações polêmicas" | "Bolsonaro: declarações polêmicas — contexto e impactos" |

### 🎯 Variações por Hash:
- **Hash 0:** "O que muda com {base}"
- **Hash 1:** "{base} — contexto e impactos"
- **Hash 2:** "{base}: pontos-chave e próximos passos"
- **E assim por diante...**

## ✅ Validação Final

### ✅ Critérios de Sucesso:
- [ ] Portal removido
- [ ] Colunista substituído
- [ ] Máximo 120 caracteres
- [ ] SEO otimizado
- [ ] Linguagem natural
- [ ] Não plagiado
- [ ] Único e diferenciado
