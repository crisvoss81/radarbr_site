# SimilarSiteFinder - Sistema Completo de Busca de Sites Similares

## 🎯 Visão Geral

O **SimilarSiteFinder** é um sistema completo para encontrar sites similares usando a API do SimilarWeb, com extração automática de contatos priorizando WhatsApp comercial. O sistema evita duplicatas verificando um banco de dados e oferece uma interface web intuitiva para gerenciar todas as operações.

## ✨ Funcionalidades Principais

### 🔍 Busca Inteligente
- **Integração SimilarWeb**: Usa a API oficial do SimilarWeb para encontrar sites similares
- **Filtros Avançados**: Por país, categoria, métricas de tráfego
- **Parâmetros Configuráveis**: Número máximo de resultados, timeout, etc.

### 📱 Extração de Contatos Prioritária
- **WhatsApp Comercial**: Prioriza contatos comerciais do WhatsApp
- **Múltiplos Tipos**: Email, telefone, redes sociais
- **Análise Inteligente**: Determina tipo de contato baseado no contexto
- **Validação**: Limpa e valida números de telefone automaticamente

### 🗄️ Sistema de Banco de Dados
- **Evita Duplicatas**: Verifica se site já existe antes de adicionar
- **Métricas Detalhadas**: Armazena dados do SimilarWeb (visitas, bounce rate, etc.)
- **Histórico Completo**: Rastreia todas as buscas realizadas
- **Status de Sites**: Ativo, inativo, bloqueado

### 🌐 Interface Web Moderna
- **Dashboard**: Estatísticas em tempo real
- **Busca Interativa**: Formulário com progresso em tempo real
- **Listagem de Sites**: Filtros e busca por texto
- **Detalhes Completos**: Página individual para cada site
- **Exportação**: Excel, CSV, JSON

### ⚙️ Sistema de Filtros
- **Filtros Salvos**: Crie e reutilize configurações de busca
- **Parâmetros Avançados**: Visitas mínimas/máximas, bounce rate, etc.
- **Gerenciamento**: Interface para criar, editar e deletar filtros

## 🚀 Instalação Rápida

### 1. Clone e Configure
```bash
git clone <seu-repositorio>
cd similar_site_finder
python setup.py
```

### 2. Configure o Ambiente
```bash
# Edite o arquivo .env
SIMILARWEB_API_KEY=sua_chave_api_similarweb
FLASK_SECRET_KEY=sua_chave_secreta_muito_segura
```

### 3. Execute o Sistema
```bash
python app.py
```

### 4. Acesse a Interface
```
http://localhost:5000
```

## 📊 Como Usar

### 1. **Busca Básica**
- Acesse `/search`
- Digite o site de referência (ex: `exemplo.com.br`)
- Configure país e número de resultados
- Marque "Extrair Contatos" para busca automática
- Clique em "Iniciar Busca"

### 2. **Acompanhar Progresso**
- Barra de progresso em tempo real
- Contadores de sites encontrados, novos sites e contatos
- Tempo decorrido da busca

### 3. **Analisar Resultados**
- Visualizar sites encontrados em `/sites`
- Detalhes completos de cada site
- Contatos extraídos organizados por tipo
- Métricas do SimilarWeb

### 4. **Exportar Dados**
- Exportar para Excel, CSV ou JSON
- Filtrar por categoria, país, etc.
- Até 10.000 registros por exportação

## 🔧 Configuração Avançada

### Variáveis de Ambiente (.env)
```env
# API SimilarWeb (obrigatório)
SIMILARWEB_API_KEY=sua_chave_api_similarweb

# Banco de dados
DATABASE_URL=sqlite:///sites.db

# Flask
FLASK_SECRET_KEY=sua_chave_secreta_muito_segura
DEBUG=True

# Configurações de busca
DEFAULT_COUNTRY=BR
MAX_RESULTS=50
REQUEST_TIMEOUT=30

# Configurações de extração de contatos
CONTACT_TIMEOUT=10
MAX_CONTACTS=10
```

### Personalização de Extração de Contatos

O sistema pode ser personalizado editando `contact_extractor.py`:

```python
# Adicionar novos padrões de WhatsApp
self.whatsapp_patterns = [
    r'whatsapp[:\s]*(\+?[\d\s\-\(\)]{10,})',
    r'wa\.me/(\d+)',
    # Adicione seus padrões aqui
]

# Adicionar palavras-chave comerciais
self.commercial_keywords = [
    'comercial', 'vendas', 'sales',
    # Adicione suas palavras-chave
]
```

## 📁 Estrutura do Projeto

```
similar_site_finder/
├── app.py                 # Aplicação Flask principal
├── config.py              # Configurações do sistema
├── models.py              # Modelos de banco de dados
├── similarweb_api.py      # Integração SimilarWeb API
├── contact_extractor.py   # Extrator de contatos
├── database.py            # Configuração do banco
├── setup.py               # Script de inicialização
├── requirements.txt       # Dependências Python
├── env_example.txt        # Exemplo de configuração
├── templates/             # Templates HTML
│   ├── index.html         # Página inicial
│   ├── search.html        # Página de busca
│   ├── results.html       # Página de resultados
│   ├── sites.html         # Listagem de sites
│   ├── site_detail.html   # Detalhes do site
│   ├── dashboard.html      # Dashboard
│   └── filters.html       # Gerenciamento de filtros
├── static/                # Arquivos estáticos
└── README.md              # Documentação
```

## 🔑 APIs Necessárias

### SimilarWeb API
- **Obrigatória**: Para buscar sites similares
- **Registro**: https://www.similarweb.com/corp/api/
- **Planos**: Gratuito (limitado) e pagos
- **Documentação**: https://docs.similarweb.com/

### APIs Opcionais
- **Validação de Telefone**: Para melhorar precisão
- **Geolocalização**: Para determinar país do número
- **Email Validation**: Para validar emails extraídos

## 📈 Métricas e Estatísticas

O sistema coleta e exibe:

- **Sites Totais**: Quantidade de sites no banco
- **Sites Ativos**: Sites com status ativo
- **Contatos WhatsApp**: Contatos do WhatsApp encontrados
- **Total de Contatos**: Todos os tipos de contato
- **Buscas Recentes**: Histórico das últimas buscas
- **Tempo de Execução**: Duração das buscas

## 🛠️ Desenvolvimento

### Executar em Modo Desenvolvimento
```bash
export FLASK_ENV=development
export DEBUG=True
python app.py
```

### Executar Testes
```bash
python -m pytest tests/
```

### Migrações de Banco
```bash
flask db init
flask db migrate -m "Descrição da migração"
flask db upgrade
```

## 🔒 Segurança

- **Rate Limiting**: Controle de requisições para SimilarWeb
- **Validação de Entrada**: Sanitização de dados de entrada
- **Timeout**: Evita travamentos em sites lentos
- **Headers Realistas**: Simula navegador real
- **Logs Detalhados**: Rastreamento de erros e atividades

## 📞 Suporte e Contribuição

### Reportar Problemas
- Abra uma issue no repositório
- Inclua logs de erro e configurações
- Descreva passos para reproduzir

### Contribuir
- Fork o repositório
- Crie uma branch para sua feature
- Faça commit das mudanças
- Abra um Pull Request

### Roadmap
- [ ] Integração com outras APIs de análise
- [ ] Sistema de notificações
- [ ] API REST completa
- [ ] Interface mobile
- [ ] Análise de sentimentos dos sites
- [ ] Integração com CRM

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.

## 🙏 Agradecimentos

- **SimilarWeb**: Pela API poderosa de análise de sites
- **Flask**: Framework web Python
- **Bootstrap**: Interface responsiva
- **Font Awesome**: Ícones modernos

---

**SimilarSiteFinder** - Encontre sites similares com inteligência! 🚀
