# rb_portal/templatetags/rb_filters.py
import re
from django import template
from django.utils.html import strip_tags
from django.utils.text import Truncator

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


_BULLET_RE = re.compile(r'<li[^>]*>(.*?)</li>', re.IGNORECASE | re.DOTALL)

@register.filter
def meta_description_from_highlights(html: str, length: int = 160) -> str:
    """Gera meta description a partir dos highlights (<li>) ou do primeiro parágrafo.
    Retorna texto limpo e truncado ao comprimento indicado.
    """
    if not html:
        return ""
    bullets = _BULLET_RE.findall(html or '')
    text = ' '.join(strip_tags(b).strip() for b in bullets[:3] if strip_tags(b).strip())
    if not text:
        # fallback: primeiro parágrafo
        first_p = re.search(r'<p[^>]*>(.*?)</p>', html, re.IGNORECASE | re.DOTALL)
        if first_p:
            text = strip_tags(first_p.group(1)).strip()
    return Truncator(text).chars(length)

@register.filter
def split_content_sections(content):
    """Divide o conteúdo em duas seções para SEO e AdSense"""
    from django.utils.safestring import mark_safe
    import re
    
    # Encontrar todos os H2 no conteúdo
    h2_pattern = r'<h2[^>]*>(.*?)</h2>'
    h2_matches = list(re.finditer(h2_pattern, content, re.IGNORECASE | re.DOTALL))
    
    if len(h2_matches) < 2:
        # Se não há pelo menos 2 H2s, retornar conteúdo original
        return mark_safe(content)
    
    # Dividir no meio (segundo H2)
    split_point = h2_matches[1].start()
    
    section1 = content[:split_point]
    section2 = content[split_point:]
    
    # Criar HTML com banner AdSense entre as seções
    adsense_banner = '''
    <div class="ad-slot ad-slot--content-middle" style="margin: 2rem 0; text-align: center;">
        <ins class="adsbygoogle"
             style="display:block"
             data-ad-client="ca-pub-4840700734"
             data-ad-slot="4840700734"
             data-ad-format="auto"
             data-full-width-responsive="true"></ins>
        <script>
             (adsbygoogle = window.adsbygoogle || []).push({});
        </script>
    </div>
    '''
    
    return mark_safe(f'{section1}{adsense_banner}{section2}')


