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
    title = topic.strip().capitalize()
    dek = f"Entenda, de forma objetiva, os principais pontos sobre {topic.strip()}."
    html = f"""
<h2>Resumo rápido</h2>
<p>Este conteúdo traz uma visão direta sobre <strong>{topic}</strong>: contexto, principais fatos e o que observar a seguir.</p>
<h2>Principais pontos</h2>
<ul>
  <li>O que é: definição breve do tema.</li>
  <li>Por que importa: impacto para o público.</li>
  <li>Próximos passos: o que acompanhar.</li>
</ul>
<h2>Perguntas frequentes</h2>
<h3>O que é {topic}?</h3>
<p>Resumo simples e claro.</p>
<h3>Qual o impacto?</h3>
<p>Impactos práticos no dia a dia das pessoas.</p>
"""
    return {"title": title[:140], "dek": dek[:220], "html": html.strip(), "image_url": None}


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
        "Você é um redator sênior de portal de notícias brasileiro. "
        "Escreva em PT-BR, direto ao ponto, tom informativo, com práticas de SEO. "
        "Nunca invente dados específicos (datas, placares, preços). Quando necessário, use linguagem geral."
    )

    user = f"""
Gere um ARTIGO EM JSON sobre o tópico entre <topic>…</topic>. Regras:

<topic>{topic.strip()}</topic>

[OBJETIVO]
- Otimizar para SEO e intenção de busca (informacional).
- Tamanho alvo: >= {min_words} palavras (conteúdo substancial, sem enrolação).
- Linguagem simples, parágrafos de 2–4 linhas.

[ESTRUTURA]
- Retorne **apenas** um JSON com campos: "title", "dek", "html".
- title: 55–70 caracteres, claro e sem clickbait.
- dek: 140–200 caracteres, resumo chamativo com a palavra-chave principal.
- html: conteúdo em HTML sem <html>/<body>, seguindo:

<h2>O que é/Contexto</h2>
<p>…</p>
<h2>Panorama atual</h2>
<p>…</p>
<h2>Principais pontos</h2>
<ul><li>…</li><li>…</li></ul>
<h2>Impactos para o público</h2>
<p>…</p>
<h2>Perguntas frequentes</h2>
<h3>Pergunta 1</h3><p>Resposta curta e útil.</p>
<h3>Pergunta 2</h3><p>Resposta curta e útil.</p>

[REGRAS]
- Não use marcações Markdown; apenas HTML nos trechos de conteúdo.
- Não coloque tag <h1> no corpo (o template já cuida do H1).
- Não cite que foi gerado por IA.
- Sem links externos.
- NUNCA retorne nada além do JSON final.
"""

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.7,
            max_tokens=2000,
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
    html = (data.get("html") or "").strip()

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