# SimilarSiteFinder - Sistema de Busca de Sites Similares

## 📋 Descrição
Sistema para encontrar sites similares usando SimilarWeb, verificar duplicatas em banco de dados e extrair contatos (priorizando WhatsApp comercial).

## 🚀 Instalação

### 1. Clone o repositório
```bash
git clone <seu-repositorio>
cd similar_site_finder
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

### 4. Execute o sistema
```bash
python app.py
```

## 🔧 Configuração

### Variáveis de Ambiente (.env)
```env
SIMILARWEB_API_KEY=sua_chave_api_similarweb
DATABASE_URL=sqlite:///sites.db
FLASK_SECRET_KEY=sua_chave_secreta
DEBUG=True
```

## 📊 Funcionalidades

- ✅ Busca sites similares via SimilarWeb API
- ✅ Verificação de duplicatas em banco de dados
- ✅ Extração automática de contatos
- ✅ Priorização de WhatsApp comercial
- ✅ Interface web para gerenciamento
- ✅ Exportação para Excel/CSV
- ✅ Sistema de filtros avançados

## 🎯 Como Usar

1. **Acesse a interface web**: http://localhost:5000
2. **Digite o site de referência**: ex: exemplo.com.br
3. **Configure os parâmetros**: país, categoria, número de resultados
4. **Execute a busca**: O sistema encontrará sites similares
5. **Revise os resultados**: Verifique contatos extraídos
6. **Exporte os dados**: Baixe em Excel ou CSV

## 📁 Estrutura do Projeto

```
similar_site_finder/
├── app.py                 # Aplicação Flask principal
├── config.py              # Configurações
├── models.py              # Modelos de banco de dados
├── similarweb_api.py      # Integração SimilarWeb
├── contact_extractor.py   # Extrator de contatos
├── database.py            # Configuração do banco
├── templates/             # Templates HTML
├── static/               # CSS, JS, imagens
├── requirements.txt       # Dependências Python
└── README.md             # Este arquivo
```

## 🔑 API Keys Necessárias

- **SimilarWeb API**: https://www.similarweb.com/corp/api/
- **Opcional**: APIs de validação de telefone/email

## 📞 Suporte

Para dúvidas ou problemas, abra uma issue no repositório.
