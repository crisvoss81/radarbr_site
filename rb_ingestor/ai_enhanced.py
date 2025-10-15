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

def generate_enhanced_article(topic: str, news_context: Optional[Dict] = None, min_words: int = 800) -> Dict:
    """
    Gera artigo melhorado baseado em contexto específico
    """
    if not OpenAI:
        return None
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Criar prompt específico baseado no contexto
    if news_context:
        prompt = create_news_specific_prompt(topic, news_context, min_words)
    else:
        prompt = create_topic_specific_prompt(topic, min_words)
    
    try:
        response = client.chat.completions.create(
            model=MODEL_DEFAULT,
            messages=[
                {
                    "role": "system",
                    "content": "Você é um jornalista especializado brasileiro com expertise em análise de notícias e criação de conteúdo SEO otimizado. Seu trabalho é criar artigos informativos, precisos e envolventes baseados em fatos reais."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        content = response.choices[0].message.content
        
        # Processar resposta
        return process_enhanced_response(content, topic, news_context)
        
    except Exception as e:
        print(f"Erro na IA melhorada: {e}")
        return None

def create_news_specific_prompt(topic: str, news_context: Dict, min_words: int) -> str:
    """Cria prompt específico baseado em notícia real"""
    
    title = news_context.get('title', '')
    description = news_context.get('description', '')
    source = news_context.get('source', '')
    
    return f"""
Crie um artigo jornalístico completo e envolvente baseado nesta notícia específica:

INFORMAÇÕES DA NOTÍCIA:
- Tópico: {topic}
- Título Original: {title}
- Descrição: {description}
- Fonte: {source}

REQUISITOS OBRIGATÓRIOS:
- MÍNIMO de {min_words} palavras (ideal: {min_words + 200})
- Artigo baseado nos FATOS REAIS da notícia, não genérico
- Linguagem jornalística profissional e envolvente
- ESTRUTURA OBRIGATÓRIA: EXATAMENTE 2 subtítulos H2 (não mais, não menos)
- Parágrafos informativos e desenvolvidos (4-5 frases cada)
- Incluir listas quando apropriado
- Densidade de palavra-chave natural (1-2%)
- Contexto brasileiro quando relevante
- Tom informativo mas acessível

ESTRUTURA OBRIGATÓRIA (EXATAMENTE 2 H2):
1. **Primeiro H2** (4-5 parágrafos informativos)
   - Contextualize a notícia específica
   - Explique por que é importante agora
   - Mencione os fatos principais
   - Desenvolva cada ponto com detalhes

2. **Segundo H2** (4-5 parágrafos informativos)
   - Detalhe os acontecimentos específicos
   - Cite informações da fonte quando possível
   - Explique o contexto histórico se relevante
   - Desenvolva análises e implicações

IMPORTANTE - DESENVOLVIMENTO DE CONTEÚDO:
- NÃO finalize antes de atingir o mínimo de {min_words} palavras
- Desenvolva cada parágrafo com 4-5 frases completas
- Seja detalhado e informativo
- Use transições naturais entre parágrafos

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

def create_topic_specific_prompt(topic: str, min_words: int) -> str:
    """Cria prompt específico para tópico sem notícia"""
    
    return f"""
Crie um artigo jornalístico completo e envolvente sobre o tópico: "{topic}"

REQUISITOS OBRIGATÓRIOS:
- Mínimo de {min_words} palavras (ideal: {min_words + 200})
- Artigo informativo e atualizado sobre o tópico
- Linguagem jornalística profissional e envolvente
- Estrutura com subtítulos H2 e H3 informativos
- Parágrafos curtos e objetivos (máximo 4 linhas)
- Incluir listas quando apropriado
- Densidade de palavras-chave natural (1-2%)
- Contexto brasileiro quando relevante
- Tom informativo mas acessível

ESTRUTURA OBRIGATÓRIA:
1. **Introdução Impactante** (2-3 parágrafos)
   - Contextualize o tópico
   - Explique por que é relevante agora
   - Apresente os pontos principais

2. **Desenvolvimento Principal** (4-5 parágrafos)
   - Detalhe os aspectos principais do tópico
   - Explique o contexto histórico se relevante
   - Forneça informações atualizadas

3. **Análise e Impacto** (3-4 parágrafos)
   - Analise as implicações do tópico
   - Explique quem é afetado e como
   - Discuta possíveis consequências

4. **Contexto Brasileiro** (2-3 parágrafos)
   - Como isso afeta o Brasil especificamente
   - Situação atual no Brasil
   - Impacto na sociedade brasileira

5. **Perspectivas Futuras** (2-3 parágrafos)
   - O que esperar nos próximos meses
   - Possíveis desenvolvimentos
   - Tendências futuras

6. **Conclusão Forte** (1-2 parágrafos)
   - Resumo dos pontos principais
   - Importância do tópico
   - Chamada para acompanhamento

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
        r'\{[^{}]*"title"[^{}]*\}',  # JSON simples
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
        return content[start:end+1]
    
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
