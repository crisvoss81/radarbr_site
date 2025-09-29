# rb_portal/templatetags/rb_filters.py
import re
from django import template
from django.utils.html import strip_tags

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
