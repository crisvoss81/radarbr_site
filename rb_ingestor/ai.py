# rb_ingestor/ai.py
"""
Gera artigo SEO em PT-BR a partir de um tópico:
- Retorna dict: {title, dek, html, image_url}
- Estrutura: H2/H3, parágrafos curtos, listas e FAQ
- Sem uso de proxies; usa OPENAI_API_KEY/OPENAI_MODEL
- Integração com sistema de busca de imagens
"""
from __future__ import annotations
import os
import json
import re
from typing import Dict
from html import unescape

try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # o caller deve tratar se a lib não estiver instalada

# Importar sistema de busca de imagens
try:
    from .image_search import find_image_for_news
    from .image_cache import image_cache
except ImportError:
    find_image_for_news = None
    image_cache = None


MODEL_DEFAULT = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def _first_json_blob(text: str) -> str | None:
    """
    CORRIGIDO: Extrai o primeiro bloco JSON do texto de forma mais robusta,
    sem usar regex recursivo.
    """
    if not text:
        return None
    
    # Encontra o primeiro '{' e o último '}'
    start_index = text.find('{')
    end_index = text.rfind('}')
    
    if start_index != -1 and end_index != -1 and end_index > start_index:
        json_str = text[start_index : end_index + 1]
        try:
            # Tenta validar se é um JSON válido antes de retornar
            json.loads(json_str)
            return json_str
        except json.JSONDecodeError:
            return None # Não é um JSON válido
            
    return None


def _fallback_article(topic: str) -> Dict[str, str]:
    title = f"Tudo sobre {topic.strip().title()}: Guia Completo"
    dek = f"Descubra os principais aspectos de {topic.strip()} e entenda como isso impacta o Brasil. Informações essenciais para você ficar por dentro."
    html = f"""
<h2>Introdução</h2>
<p>Quando falamos sobre <strong>{topic}</strong>, estamos tratando de um tema que tem ganhado cada vez mais relevância no cenário brasileiro. Vamos explorar os principais pontos para você entender melhor essa questão.</p>

<h2>O que você precisa saber</h2>
<p>Para compreender completamente {topic}, é importante entender alguns conceitos fundamentais e como eles se aplicam à nossa realidade.</p>

<h2>Principais aspectos</h2>
<ul>
  <li><strong>Definição:</strong> O que realmente significa {topic} na prática</li>
  <li><strong>Relevância:</strong> Por que isso importa para os brasileiros</li>
  <li><strong>Impacto:</strong> Como isso afeta o dia a dia das pessoas</li>
  <li><strong>Perspectivas:</strong> O que esperar para o futuro</li>
</ul>

<h2>Impacto no Brasil</h2>
<p>No contexto brasileiro, {topic} tem se mostrado um fator importante que merece atenção. Vamos entender melhor como isso se manifesta em nosso país.</p>

<h2>Perguntas Frequentes</h2>
<h3>O que é {topic}?</h3>
<p>Uma explicação clara e objetiva sobre o conceito, sem complicações desnecessárias.</p>

<h3>Como isso afeta o brasileiro?</h3>
<p>Os impactos práticos e diretos na vida das pessoas, com exemplos reais.</p>

<h3>O que esperar?</h3>
<p>Uma visão sobre as tendências e desenvolvimentos futuros relacionados ao tema.</p>
"""
    return {"title": title[:140], "dek": dek[:220], "html": html.strip(), "image_url": None}
def _sanitize_generated_html(raw_html: str) -> str:
    """Remove estilos inline e atributos que causam recuos/margens indevidas.
    Mantém apenas tags semânticas básicas (p, h2/h3, ul/ol/li, strong, em, a sem href externo).
    """
    if not raw_html:
        return ""
    html = unescape(raw_html).strip()

    # Remover estilos inline problemáticos (margin, padding, text-indent, width/height)
    html = re.sub(r'\sstyle="[^"]*(margin|padding|text-indent|width|height)[^"]*"', "", html, flags=re.IGNORECASE)

    # Remover align, class genérica e id que podem vir do modelo
    html = re.sub(r'\s(align|id|class)="[^"]*"', "", html, flags=re.IGNORECASE)

    # Remover <span> vazios ou apenas de estilo
    html = re.sub(r'<span>(.*?)</span>', r'\1', html, flags=re.IGNORECASE|re.DOTALL)

    # Normalizar H1->H2 (garantia extra)
    html = re.sub(r'<\/?h1>', lambda m: '<h2>' if m.group(0)[1] != '/' else '</h2>', html, flags=re.IGNORECASE)

    # Remover tags estranhas comuns
    html = re.sub(r'</?(section|article|header|footer|figure|figcaption)>', '', html, flags=re.IGNORECASE)

    # Remover múltiplas quebras/linhas
    html = re.sub(r'\n+', '\n', html)

    return html.strip()


def generate_article(topic: str, *, model: str | None = None, min_words: int = 700) -> Dict[str, str]:
    """
    Gera um artigo otimizado para SEO (PT-BR).
    - topic: assunto principal
    - model: opcional (default via env)
    - min_words: alvo mínimo de palavras no corpo do texto
    """
    if not topic or not isinstance(topic, str):
        return _fallback_article(topic or "Assunto")

    if OpenAI is None:
        return _fallback_article(topic)

    client = OpenAI()  # sem proxies; pega OPENAI_API_KEY do ambiente
    model = model or MODEL_DEFAULT

    system = (
        "Você é um jornalista brasileiro experiente escrevendo para um portal de notícias. "
        "Escreva com tom profissional mas acessível, como se estivesse explicando para um leitor comum. "
        "Evite linguagem excessivamente técnica ou acadêmica. "
        "Não use expressões forçadas ou jargões de marketing. "
        "Seja direto, informativo e natural. "
        "Nunca invente números, datas ou fatos específicos. "
        "Se não souber algo, seja honesto sobre as limitações. "
        "Foque em informar com clareza e objetividade."
    )

    user = f"""
Crie um artigo jornalístico completo sobre o tópico abaixo.

TÓPICO: {topic.strip()}

FORMATO (JSON):
{{
    "title": "Título informativo e direto (50-70 caracteres)",
    "dek": "Resumo claro do artigo (120-150 caracteres)",
    "html": "Conteúdo em HTML sem tags <html>/<body>"
}}

ESTRUTURA DO CONTEÚDO (HTML):
<h2>Subtítulo 1</h2>
<p>Conteúdo relevante...</p>

<h2>Subtítulo 2</h2>
<p>Conteúdo relevante...</p>

<p>Continue com mais parágrafos, se necessário.</p>

DIRETRIZES:
- Mínimo de {min_words} palavras no total
- Escreva como um jornalista profissional explicando para o leitor comum
- Use linguagem clara e objetiva
- Evite jargões e expressões exageradas
- Não force palavras-chave - seja natural
- Não invente fatos, números ou datas específicas
- Não use expressões de IA como "vale a pena", "é essencial", "é fundamental"
- Não crie perguntas frequentes artificiais
- Mantenha tom informativo e equilibrado
- Retorne APENAS o JSON, sem explicações antes ou depois
"""

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.8,  # Mais criatividade para evitar repetição
            max_tokens=3000,  # Mais tokens para conteúdo mais longo
            top_p=0.9,       # Diversidade de vocabulário
            frequency_penalty=0.3,  # Penaliza repetições
            presence_penalty=0.2,   # Incentiva novos tópicos
        )
        content = resp.choices[0].message.content or ""
    except Exception:
        return _fallback_article(topic)

    blob = _first_json_blob(content) or ""
    try:
        data = json.loads(blob)
    except Exception:
        return _fallback_article(topic)

    title = (data.get("title") or topic).strip()
    dek = (data.get("dek") or f"Saiba os pontos essenciais sobre {topic}.").strip()
    html = _sanitize_generated_html((data.get("html") or "").strip())

    # pequenos saneamentos
    title = re.sub(r"\s+", " ", title)[:140]
    dek = re.sub(r"\s+", " ", dek)[:220]

    # garante algumas seções mínimas se o modelo vier curto
    if "<h2" not in html:
        html = _fallback_article(topic)["html"]

    # Buscar imagem para o artigo
    image_url = None
    if find_image_for_news and image_cache:
        # Verificar cache primeiro
        cached_url = image_cache.get(title, topic)
        if cached_url:
            image_url = cached_url
        else:
            # Buscar nova imagem
            image_url = find_image_for_news(title, html, topic)
            if image_url:
                # Armazenar no cache
                image_cache.set(title, image_url, topic, {
                    'source': 'ai_generated',
                    'topic': topic
                })

    return {"title": title, "dek": dek, "html": html, "image_url": image_url}