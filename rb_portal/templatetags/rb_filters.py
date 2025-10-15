# rb_portal/templatetags/rb_filters.py
import re
from django import template
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

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
    Divide o conteúdo HTML em duas seções baseadas em H2 tags
    e insere um banner AdSense entre elas.
    """
    if not html:
        return html
    
    # Banner AdSense HTML
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
    
    # Encontrar todas as tags H2
    h2_pattern = r'<h2[^>]*>.*?</h2>'
    h2_matches = list(re.finditer(h2_pattern, html, re.IGNORECASE | re.DOTALL))
    
    if len(h2_matches) < 2:
        # Se não há pelo menos 2 H2s, retorna o conteúdo original
        return html
    
    # Pegar o primeiro H2 como divisor
    first_h2_end = h2_matches[0].end()
    
    # Dividir o conteúdo
    first_section = html[:first_h2_end]
    second_section = html[first_h2_end:]
    
    # Combinar com o banner no meio
    result = first_section + adsense_banner + second_section
    
    return mark_safe(result)

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
