# rb_portal/templatetags/rb_filters.py
import re
from django import template
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from typing import List
from django.conf import settings

register = template.Library()

_DEK_RE = re.compile(
    r'<p[^>]*class="[^"]*\bdek\b[^"]*"[^>]*>(.*?)</p>',
    re.IGNORECASE | re.DOTALL
)

@register.filter
def extract_dek(html: str) -> str:
    """Retorna o texto da primeira <p class="dek">...</p> do conteúdo."""
    if not html:
        return ""
    m = _DEK_RE.search(html)
    if not m:
        return ""
    return strip_tags(m.group(1)).strip()

@register.filter
def split_content_sections(html: str) -> str:
    """
    Retorna o conteúdo HTML sem modificações.
    (Função mantida para compatibilidade, mas não divide mais o conteúdo)
    """
    if not html:
        return html
    
    # Retornar conteúdo original sem divisão ou banner
    return mark_safe(html)

@register.filter
def meta_description_from_highlights(html: str) -> str:
    """
    Gera uma meta description baseada nos destaques do artigo.
    """
    if not html:
        return ""
    
    # Extrair texto limpo
    clean_text = strip_tags(html)
    
    # Pegar as primeiras 160 caracteres
    description = clean_text[:160]
    
    # Se cortou no meio de uma palavra, cortar na palavra anterior
    if len(clean_text) > 160:
        last_space = description.rfind(' ')
        if last_space > 120:  # Só cortar se não ficar muito curto
            description = description[:last_space]
    
    return description + "..." if len(clean_text) > 160 else description


@register.filter
def split_lines(value: str) -> list:
    """Divide um texto em linhas não vazias."""
    if not value:
        return []
    return [line.strip() for line in value.splitlines() if line.strip()]


@register.filter
def youtube_id(url: str) -> str:
    """Extrai o ID de um vídeo do YouTube a partir de uma URL."""
    if not url:
        return ""
    patterns = [
        r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/v/([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        m = re.search(pattern, url)
        if m:
            return m.group(1)
    # Como fallback, tentar pegar parâmetro v
    m = re.search(r'[?&]v=([a-zA-Z0-9_-]{11})', url)
    return m.group(1) if m else ""


@register.simple_tag
def render_youtube_embeds(urls_text: str) -> str:
    """Monta HTML de embeds do YouTube a partir de texto com URLs (uma por linha)."""
    if not urls_text:
        return ""
    lines = [line.strip() for line in urls_text.splitlines() if line.strip()]
    if not lines:
        return ""
    items_html = []
    for line in lines:
        vid = youtube_id(line)
        if not vid:
            continue
        items_html.append(
            f'''<div class="youtube-video-container" style="text-align:center;">
  <div class="video-wrapper" style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; background: #000;">
    <iframe
      src="https://www.youtube.com/embed/{vid}?rel=0&modestbranding=1&playsinline=1"
      style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
      referrerpolicy="strict-origin-when-cross-origin"
      allowfullscreen
      title="Vídeo relacionado"></iframe>
  </div>
</div>'''
        )
    if not items_html:
        return ""
    block = '<section class="post-videos" style="margin: 2rem 0;">\n  <h2>Vídeos relacionados</h2>\n  <div class="video-list" style="display: grid; grid-template-columns: 1fr; gap: 1.5rem;">\n' + "\n".join(items_html) + "\n  </div>\n</section>"
    return mark_safe(block)


@register.filter(name="inject_between_sections")
def inject_between_sections(html: str, injection_html: str) -> str:
    """
    Insere injection_html entre a primeira e a segunda parte do artigo
    (logo antes do banner do split). Se não houver 2 H2, insere após
    o primeiro parágrafo.
    """
    if not html or not injection_html:
        return html

    # Encontrar H2s
    h2_pattern = r'<h2[^>]*>.*?</h2>'
    h2_matches = list(re.finditer(h2_pattern, html, re.IGNORECASE | re.DOTALL))

    if len(h2_matches) >= 2:
        # Inserir imediatamente antes do segundo H2
        insert_at = h2_matches[1].start()
        return mark_safe(html[:insert_at] + injection_html + html[insert_at:])

    # Fallback: após o primeiro parágrafo
    p_close = html.lower().find('</p>')
    if p_close != -1:
        insert_at = p_close + len('</p>')
        return mark_safe(html[:insert_at] + injection_html + html[insert_at:])

    # Último fallback: ao final
    return mark_safe(html + injection_html)
