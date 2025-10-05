import markdown
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name="render_markdown")
@stringfilter
def render_markdown(value):
    return mark_safe(markdown.markdown(value))