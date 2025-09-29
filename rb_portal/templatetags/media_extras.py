from django import template

register = template.Library()

@register.filter
def file_exists(fieldfile):
    """
    True somente se o campo possui nome e o arquivo existe no storage.
    Uso: {% if obj.imagem|file_exists %} ... {% endif %}
    """
    try:
        return bool(fieldfile and getattr(fieldfile, "name", "") and fieldfile.storage.exists(fieldfile.name))
    except Exception:
        return False
