# rb_ingestor/ai_enhanced.py
"""
Sistema de IA melhorado para geração de conteúdo específico e relevante
"""
from __future__ import annotations
import os
import json
import re
from typing import Dict, Optional
from html import unescape

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

MODEL_DEFAULT = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def generate_enhanced_article(topic: str, news_context: Optional[Dict] = None, min_words: int = 800, writing_style: str = None) -> Dict:
    """
    Gera artigo melhorado baseado em contexto específico
    """
    if not OpenAI:
        return None
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Selecionar estilo de escrita aleatório se não especificado
    if not writing_style:
        from rb_ingestor.writing_styles import writing_style_manager
        writing_style = writing_style_manager.get_random_style()
    
    # Criar prompt específico baseado no contexto
    if news_context:
        prompt = create_news_specific_prompt(topic, news_context, min_words, writing_style)
    else:
        prompt = create_topic_specific_prompt(topic, min_words, writing_style)
    
    try:
        response = client.chat.completions.create(
            model=MODEL_DEFAULT,
            messages=[
                {
                    "role": "system",
                    "content": f"""Você é um jornalista especializado brasileiro escrevendo para um portal de notícias real.

REGRAS FUNDAMENTAIS:
1. Escreva como uma PESSOA REAL, não como IA
2. Cada artigo deve ter estrutura ÚNICA e DIFERENTE
3. VARIE sempre: subtítulos, tamanho de parágrafos, início de frases
4. Evite padrões repetitivos ao máximo
5. Seja NATURAL, HUMANO e ESPECÍFICO baseado na notícia real
6. Não use expressões genéricas de IA
7. Escreva como se estivesse contando uma história interessante"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.9,  # Mais criatividade para variação
            max_tokens=4000,
            top_p=0.95,  # Mais diversidade
            frequency_penalty=0.5,  # Penaliza repetições (evita padrões)
            presence_penalty=0.3  # Incentiva novos tópicos e variações
        )
        
        content = response.choices[0].message.content
        
        # Processar resposta
        return process_enhanced_response(content, topic, news_context)
        
    except Exception as e:
        print(f"Erro na IA melhorada: {e}")
        return None

def create_news_specific_prompt(topic: str, news_context: Dict, min_words: int, writing_style: str = None) -> str:
    """Cria prompt específico baseado em notícia real"""
    
    title = news_context.get('title', '')
    description = news_context.get('description', '')
    source = news_context.get('source', '')
    
    # Obter informações do estilo de escrita
    style_prompt = ""
    if writing_style:
        from rb_ingestor.writing_styles import writing_style_manager
        style_prompt = writing_style_manager.create_style_prompt(writing_style, topic, min_words)
    
    return f"""
{style_prompt}

Crie um artigo completo e envolvente baseado nesta notícia específica:

INFORMAÇÕES DA NOTÍCIA:
- Tópico: {topic}
- Título Original: {title}
- Descrição: {description}
- Fonte: {source}

REQUISITOS OBRIGATÓRIOS:
- MÍNIMO de {min_words} palavras (ideal: {min_words + 200})
- Artigo baseado nos FATOS REAIS da notícia, não genérico
- Linguagem jornalística profissional e envolvente
- VARIAÇÃO DE ESTRUTURA: EVITE subtítulos H2 - prefira texto corrido bem estruturado (máximo 1 H2, preferencialmente 0)
- VARIE tamanhos de parágrafos: alguns curtos (2-3 frases), outros médios (4-5 frases)
- Incluir listas quando apropriado
- Densidade de palavra-chave natural (1-2%)
- Contexto brasileiro quando relevante
- Tom informativo mas acessível

CRÍTICO - EVITAR PADRÕES ARTIFICIAIS:
- ❌ NÃO use estruturas fixas como "Introdução", "Desenvolvimento", "Conclusão"
- ❌ NÃO use sempre os mesmos padrões de subtítulos
- ❌ NÃO comece parágrafos sempre da mesma forma
- ❌ NÃO termine com: "é fundamental", "vale a pena", "é essencial"
- ✅ VARIE o estilo dos subtítulos (perguntas, afirmações, descrições)
- ✅ VARIE o tamanho dos parágrafos
- ✅ Escreva como um JORNALISTA REAL, não como IA

SUBTÍTULOS (USE COM EXTREMA MODERAÇÃO):
- ⚠️ EVITE usar H2 - prefira texto corrido sem subtítulos
- Use H2 APENAS quando ABSOLUTAMENTE necessário para organização
- MÁXIMO 1 H2 por artigo (a maioria dos artigos deve ter 0 H2)
- Prefira parágrafos bem desenvolvidos sem dividir com subtítulos
- NÃO use H2 para separar seções genéricas
- Se usar H2, que seja algo ESPECÍFICO e realmente necessário

IMPORTANTE - DESENVOLVIMENTO DE CONTEÚDO:
- NÃO finalize antes de atingir o mínimo de {min_words} palavras
- VARIE tamanhos de parágrafos: alguns curtos (2-3 frases), outros médios (4-5 frases)
- Seja detalhado e informativo quando apropriado
- Use transições naturais e variadas entre parágrafos

IMPORTANTE - EVITAR PLÁGIO:
- NUNCA copie títulos de outros portais
- NUNCA mencione nomes de outros portais no título
- Sempre crie títulos originais e únicos
- Use apenas o contexto da notícia para criar conteúdo original
- Cite fontes de forma genérica (ex: "segundo fontes oficiais")
- Foque EXCLUSIVAMENTE na notícia específica mencionada
- Use informações reais da descrição fornecida
- Evite generalizações sobre o tema
- Seja preciso e factual
- Mantenha tom jornalístico profissional
- Inclua detalhes específicos quando disponíveis

CRÍTICO - CONTEÚDO ESPECÍFICO:
- SEMPRE baseie o conteúdo nos FATOS REAIS da notícia fornecida
- NÃO crie conteúdo genérico sobre o tema
- Use os detalhes específicos do título e descrição
- Se a notícia fala sobre "Tesla paga bilhões a Musk", foque NESSA notícia específica
- Se a notícia fala sobre "Anitta no Iêmen", foque NESSA viagem específica
- NUNCA generalize - seja sempre específico aos fatos da notícia

OBRIGATÓRIO - USAR DADOS ESPECÍFICOS:
- Se o título menciona "Grávida, garota de programa ligada a Neymar surge com exame de DNA"
- Foque EXCLUSIVAMENTE neste caso específico do Neymar
- Use os detalhes: grávida, garota de programa, exame de DNA
- NÃO fale genericamente sobre Neymar - fale sobre ESTE caso específico
- Se menciona "Metrópoles", "Terra", "Jornal Correio" - use essas fontes específicas
- SEMPRE seja específico aos fatos mencionados no título e descrição

FORMATO DE RESPOSTA (JSON):
{{
    "title": "Título específico e impactante baseado na notícia",
    "dek": "Descrição curta e envolvente (máximo 150 caracteres)",
    "html": "Conteúdo HTML completo com estrutura solicitada"
}}
"""

def create_topic_specific_prompt(topic: str, min_words: int, writing_style: str = None) -> str:
    """Cria prompt específico para tópico sem notícia"""
    
    # Obter informações do estilo de escrita
    style_prompt = ""
    if writing_style:
        from rb_ingestor.writing_styles import writing_style_manager
        style_prompt = writing_style_manager.create_style_prompt(writing_style, topic, min_words)
    
    return f"""
{style_prompt}

Crie um artigo completo e envolvente sobre o tópico: "{topic}"

REQUISITOS OBRIGATÓRIOS:
- Mínimo de {min_words} palavras (ideal: {min_words + 200})
- Artigo informativo e atualizado sobre o tópico
- Linguagem jornalística profissional e envolvente
- VARIAÇÃO DE ESTRUTURA: EVITE subtítulos H2 - prefira texto corrido bem estruturado (máximo 1 H2, preferencialmente 0)
- VARIE tamanhos de parágrafos: alguns curtos (2-3 frases), outros médios (4-5 frases)
- Incluir listas quando apropriado
- Densidade de palavras-chave natural (1-2%)
- Contexto brasileiro quando relevante
- Tom informativo mas acessível

CRÍTICO - EVITAR PADRÕES ARTIFICIAIS:
- ❌ NÃO use estruturas fixas como "Introdução", "Desenvolvimento", "Conclusão"
- ❌ NÃO use sempre os mesmos padrões de subtítulos
- ❌ NÃO comece parágrafos sempre da mesma forma
- ❌ NÃO termine com: "é fundamental", "vale a pena", "é essencial"
- ✅ VARIE o estilo dos subtítulos (perguntas, afirmações, descrições)
- ✅ VARIE o tamanho dos parágrafos
- ✅ Escreva como um JORNALISTA REAL, não como IA

SUBTÍTULOS (USE COM EXTREMA MODERAÇÃO):
- ⚠️ EVITE usar H2 - prefira texto corrido sem subtítulos
- Use H2 APENAS quando ABSOLUTAMENTE necessário para organização
- MÁXIMO 1 H2 por artigo (a maioria dos artigos deve ter 0 H2)
- Prefira parágrafos bem desenvolvidos sem dividir com subtítulos
- NÃO use H2 para separar seções genéricas
- Se usar H2, que seja algo ESPECÍFICO e realmente necessário

COMO ESTRUTURAR (VARIE):
- Comece de formas diferentes (não sempre "Este tema...")
- Desenvolva os pontos principais naturalmente
- Inclua contexto brasileiro quando relevante (mas integrado, não como seção obrigatória)
- Varie a forma de finalizar (nem sempre com resumo genérico)

IMPORTANTE:
- Seja específico e factual sobre o tópico
- Evite generalizações excessivas
- Mantenha tom jornalístico profissional
- Inclua informações relevantes e atualizadas
- Foque na relevância para o público brasileiro

FORMATO DE RESPOSTA (JSON):
{{
    "title": "Título específico e impactante sobre o tópico",
    "dek": "Descrição curta e envolvente (máximo 150 caracteres)",
    "html": "Conteúdo HTML completo com estrutura solicitada"
}}
"""

def process_enhanced_response(content: str, topic: str, news_context: Optional[Dict] = None) -> Dict:
    """Processa resposta da IA melhorada"""
    
    # Extrair JSON da resposta
    json_content = extract_json_from_response(content)
    
    if json_content:
        try:
            # Limpar JSON antes de parsear (remover vírgulas trailing)
            json_content = re.sub(r',\s*}', '}', json_content)
            json_content = re.sub(r',\s*]', ']', json_content)
            
            data = json.loads(json_content)
            
            # Validar e limpar dados
            title = clean_text(data.get('title', topic.title()))[:200]
            dek = clean_text(data.get('dek', ''))[:220]
            html = clean_html(data.get('html', ''))
            
            # Verificar qualidade do conteúdo
            word_count = len(html.replace('<', ' <').split())
            
            if word_count < 500:  # Muito curto
                return None
            
            return {
                'title': title,
                'dek': dek,
                'html': html,
                'word_count': word_count,
                'quality_score': calculate_quality_score(html, topic, news_context)
            }
            
        except Exception as e:
            print(f"Erro ao processar JSON: {e}")
            return None
    
    return None

def extract_json_from_response(content: str) -> Optional[str]:
    """Extrai JSON da resposta da IA"""
    
    # Procurar por blocos JSON
    patterns = [
        r'```json\s*(\{.*?\})\s*```',  # JSON em bloco de código
        r'```\s*(\{.*?\})\s*```',  # JSON em bloco genérico
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content, re.DOTALL)
        if matches:
            return matches[0]
    
    # Fallback: procurar primeiro bloco entre chaves
    start = content.find('{')
    end = content.rfind('}')
    
    if start != -1 and end != -1 and end > start:
        json_str = content[start:end+1]
        
        # Limpar JSON: remover vírgulas trailing antes de chaves de fechamento
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)
        
        return json_str
    
    return None

def clean_text(text: str) -> str:
    """Limpa texto removendo caracteres problemáticos"""
    if not text:
        return ""
    
    # Remover caracteres de controle
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Decodificar entidades HTML
    text = unescape(text)
    
    # Limpar espaços extras
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def clean_html(html: str) -> str:
    """Limpa HTML removendo tags problemáticas"""
    if not html:
        return ""
    
    # Remover tags perigosas
    dangerous_tags = ['script', 'style', 'iframe', 'object', 'embed']
    for tag in dangerous_tags:
        html = re.sub(f'<{tag}[^>]*>.*?</{tag}>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(f'<{tag}[^>]*/?>', '', html, flags=re.IGNORECASE)
    
    # Limpar atributos perigosos
    html = re.sub(r'\s+on\w+\s*=\s*["\'][^"\']*["\']', '', html, flags=re.IGNORECASE)
    
    # Limpar espaços extras
    html = re.sub(r'\s+', ' ', html)
    
    return html.strip()

def calculate_quality_score(html: str, topic: str, news_context: Optional[Dict] = None) -> int:
    """Calcula score de qualidade do conteúdo"""
    score = 0
    
    # Contar palavras
    word_count = len(html.replace('<', ' <').split())
    if word_count >= 800:
        score += 30
    elif word_count >= 600:
        score += 20
    elif word_count >= 400:
        score += 10
    
    # Verificar estrutura
    if '<h2>' in html:
        score += 15
    if '<h3>' in html:
        score += 10
    if '<ul>' in html or '<ol>' in html:
        score += 10
    
    # Verificar relevância do tópico
    topic_words = topic.lower().split()
    html_lower = html.lower()
    relevance_count = sum(1 for word in topic_words if word in html_lower)
    score += min(relevance_count * 5, 20)
    
    # Bonus para conteúdo baseado em notícia
    if news_context:
        score += 15
    
    return min(score, 100)

# Função de compatibilidade
def generate_article(topic: str, news_context: Optional[Dict] = None, min_words: int = 800) -> Optional[Dict]:
    """Função de compatibilidade com o sistema existente"""
    result = generate_enhanced_article(topic, news_context, min_words)
    
    if result:
        return {
            'title': result['title'],
            'dek': result['dek'],
            'html': result['html']
        }
    
    return None
