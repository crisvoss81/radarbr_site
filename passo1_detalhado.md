# PASSO 1: BUSCA E EXTRAÇÃO DE FONTE - ANÁLISE DETALHADA

## Fluxo Atual do Passo 1

```mermaid
flowchart TD
    A[Entrada: Tópico/Assunto] --> B[GNews.get_news\(tópico\)]
    B --> C[Primeiro resultado do Google News]
    C --> D[Verifica relevância do artigo]
    D --> E{Artigo relevante?}
    
    E -->|Não| F[Retorna None - Criar do zero]
    E -->|Sim| G[Extrai URL do Google News]
    
    G --> H[Estratégia 1: Query Parameter 'url']
    H --> I{URL válida encontrada?}
    I -->|Sim| J[Retorna URL original]
    I -->|Não| K[Estratégia 2: Seguir redirecionamentos]
    
    K --> L[GET com allow_redirects=True]
    L --> M{URL final válida?}
    M -->|Sim| N[Retorna URL resolvida]
    M -->|Não| O[Estratégia 3: Scraping HTML]
    
    O --> P[Procurar links diretos]
    P --> Q[Procurar meta og:url]
    Q --> R[Procurar URLs em JavaScript]
    R --> S[Procurar atributos data-*]
    
    S --> T[Filtrar URLs válidos]
    T --> U{URL válido encontrado?}
    U -->|Sim| V[Retorna primeiro URL válido]
    U -->|Não| W[Retorna None]
    
    J --> X[Acessar artigo original]
    N --> X
    V --> X
    W --> Y[Usar dados do Google News]
    
    X --> Z[Extrair conteúdo do artigo]
    Z --> AA{Conteúdo suficiente?}
    AA -->|Sim| BB[Retorna dados completos]
    AA -->|Não| CC[Fallback: Google News]
    
    Y --> CC
    CC --> DD[Dados básicos: título + descrição]
    
    BB --> EE[✅ Artigo original como base]
    DD --> FF[⚠️ Dados limitados do Google News]
    
    style A fill:#e1f5fe
    style EE fill:#c8e6c9
    style FF fill:#ffecb3
    style F fill:#ffcdd2
```

## Detalhamento das Estratégias

### 1. **Busca Inicial (GNews)**
```python
def _search_specific_news(self, topic):
    google_news = GNews()
    google_news.language = "pt"
    google_news.country = "BR"
    google_news.max_results = 1
    
    articles = google_news.get_news(topic)
    # Verifica se o tópico aparece no título ou descrição
    if self._is_relevant_article(topic, article):
        return article
```

### 2. **Extração de URL Original (4 Estratégias)**

#### **Estratégia 1: Query Parameter**
```python
# Extrai 'url' da query string do Google News
parsed = urlparse(google_news_url)
qs = parse_qs(parsed.query)
if 'url' in qs and qs['url']:
    candidate = qs['url'][0]
    if not self._is_google_news_url(candidate):
        return candidate
```

#### **Estratégia 2: Redirecionamentos HTTP**
```python
# Segue redirecionamentos automaticamente
response = session.get(google_news_url, allow_redirects=True)
final_url = response.url
if not self._is_google_news_url(final_url):
    return final_url
```

#### **Estratégia 3: Scraping HTML**
```python
# Procura links diretos no HTML
all_links = soup.find_all('a', href=True)
for link in all_links:
    href = link.get('href')
    if not self._is_google_news_url(href) and self._looks_like_news_url(href):
        original_links.append(href)

# Procura meta tags Open Graph
meta_tags = soup.find_all('meta')
for meta in meta_tags:
    if meta.get('property') == 'og:url':
        url = meta.get('content')
        if not self._is_google_news_url(url):
            original_links.append(url)
```

#### **Estratégia 4: JavaScript e Data Attributes**
```python
# Procura URLs em scripts JavaScript
scripts = soup.find_all('script')
for script in scripts:
    url_patterns = [
        r'https?://[^\s"\'<>]+\.(com|br|org|net)/[^\s"\'<>]*',
        r'url["\']?\s*:\s*["\']([^"\']+)["\']'
    ]
    # Extrai URLs dos padrões encontrados

# Procura atributos data-*
elements_with_data = soup.find_all(attrs=lambda attrs: 
    any(k.startswith('data-') for k in attrs.keys()))
```

### 3. **Validação de URLs**

#### **Verificações de Validade**
```python
def _is_valid_news_url(self, url):
    # URLs muito curtos não são notícias
    if len(url) < 20:
        return False
    
    # Não pode ser do Google News
    if self._is_google_news_url(url):
        return False
    
    # Deve parecer URL de notícia
    return self._looks_like_news_url(url)

def _looks_like_news_url(self, url):
    news_patterns = [
        r'/\d{4}/\d{2}/\d{2}/',  # Data YYYY/MM/DD
        r'/noticia/',             # Contém "noticia"
        r'/materia/',             # Contém "materia"
        r'/artigo/',              # Contém "artigo"
        r'\.html$',               # Termina com .html
        r'\.php$',                # Termina com .php
    ]
    # Verifica se URL corresponde a algum padrão
```

### 4. **Extração de Conteúdo**

#### **Dados Extraídos do Artigo Original**
```python
def _extract_content_from_url(self, url):
    extracted_data = {
        'url': url,
        'title': self._extract_title_from_soup(soup),
        'description': self._extract_description_from_soup(soup),
        'content': self._extract_content_from_soup(soup),
        'author': self._extract_author_from_soup(soup),
        'date': self._extract_date_from_soup(soup),
        'images': self._extract_images_from_soup(soup)
    }
    
    # Validação: conteúdo deve ter pelo menos 200 caracteres
    if extracted_data['content'] and len(extracted_data['content']) > 200:
        return extracted_data
```

## Pontos Fortes do Sistema Atual

✅ **Múltiplas estratégias** de extração de URL  
✅ **Validação robusta** de URLs  
✅ **Fallbacks inteligentes** quando falha  
✅ **Headers realistas** para evitar bloqueios  
✅ **Timeout adequado** para evitar travamentos  

## Possíveis Melhorias Identificadas

🔍 **Detecção de relevância** poderia ser mais sofisticada  
🔍 **Cache de URLs** já extraídas para evitar reprocessamento  
🔍 **Rate limiting** para evitar bloqueios por excesso de requests  
🔍 **Retry logic** para URLs que falham temporariamente  
🔍 **Logging mais detalhado** para debug  

## Próximos Passos

1. **Revisar Passo 2**: Geração de Título SEO
2. **Revisar Passo 3**: Criação de Conteúdo com IA
3. **Revisar Passo 4**: Categorização Inteligente
4. **Revisar Passo 5**: Recursos Multimídia
5. **Revisar Passo 6**: Publicação Final


