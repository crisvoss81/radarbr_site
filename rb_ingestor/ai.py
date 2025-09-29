# rb_ingestor/ai.py
"""
Gera artigo SEO em PT-BR a partir de um tópico:
- Retorna dict: {title, dek, html}
- Estrutura: H2/H3, parágrafos curtos, listas e FAQ
- Sem uso de proxies; usa OPENAI_API_KEY/OPENAI_MODEL
"""
from __future__ import annotations
import os, json, re
from typing import Dict

try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # o caller deve tratar se a lib não estiver instalada


MODEL_DEFAULT = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def _first_json_blob(text: str) -> str | None:
    """Extrai o primeiro bloco {...} de JSON válido do texto."""
    if not text:
        return None
    # busca um objeto JSON mais externo
    m = re.search(r"\{(?:[^{}]|(?R))*\}", text, flags=re.S)
    return m.group(0) if m else None


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
    return {"title": title[:140], "dek": dek[:220], "html": html.strip()}


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

    return {"title": title, "dek": dek, "html": html}
