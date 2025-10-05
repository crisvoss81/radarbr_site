# rb_portal/templatetags/markdown_extras.py
import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='render_markdown')
def render_markdown(text):
    """
    Converte texto em formato Markdown para HTML.
    """
    if not text:
        return ""
    # Converte o markdown para HTML
    html = markdown.markdown(text)
    return mark_safe(html)
