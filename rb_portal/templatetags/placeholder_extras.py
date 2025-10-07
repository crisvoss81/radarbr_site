# rb_portal/templatetags/placeholder_extras.py
from django import template

register = template.Library()

@register.simple_tag
def placeholder_class(categoria=None, size='normal'):
    """
    Gera classe CSS para placeholder baseado na categoria
    
    Uso:
    {% placeholder_class obj.categoria %}
    {% placeholder_class obj.categoria size='lg' %}
    """
    if not categoria:
        base_class = "thumb-ph"
    else:
        # Mapear slug da categoria para classe CSS
        category_map = {
            'agro': 'agro',
            'brasil': 'brasil', 
            'carros-mobilidade': 'carros',
            'cidades-rs': 'cidades',
            'ciencia-meio-ambiente': 'ciencia',
            'economia': 'economia',
            'educacao': 'educacao',
            'entretenimento': 'entretenimento',
            'esportes': 'esportes',
            'geral': 'geral',
            'justica-seguranca': 'justica',
            'loterias': 'loterias',
            'mundo': 'mundo',
            'politica': 'politica',
            'saude': 'saude',
            'tecnologia': 'tecnologia',
            'trabalho-carreira': 'trabalho',
            'turismo': 'turismo',
        }
        
        category_class = category_map.get(categoria.slug, 'geral')
        base_class = f"thumb-ph thumb-ph--{category_class}"
    
    if size == 'lg':
        base_class += " thumb-ph--lg"
    
    return base_class

@register.simple_tag
def placeholder_icon(categoria=None):
    """
    Retorna ícone SVG para categoria
    
    Uso:
    {% placeholder_icon obj.categoria %}
    """
    if not categoria:
        return "📰"
    
    # Mapear categoria para emoji/ícone
    icon_map = {
        'agro': "🌾",
        'brasil': "🇧🇷", 
        'carros-mobilidade': "🚗",
        'cidades-rs': "🏙️",
        'ciencia-meio-ambiente': "🔬",
        'economia': "💰",
        'educacao': "🎓",
        'entretenimento': "🎬",
        'esportes': "⚽",
        'geral': "📰",
        'justica-seguranca': "⚖️",
        'loterias': "🎰",
        'mundo': "🌍",
        'politica': "🏛️",
        'saude': "🏥",
        'tecnologia': "💻",
        'trabalho-carreira': "💼",
        'turismo': "✈️",
    }
    
    return icon_map.get(categoria.slug, "📰")

@register.simple_tag
def placeholder_text(categoria=None):
    """
    Retorna texto para placeholder baseado na categoria
    
    Uso:
    {% placeholder_text obj.categoria %}
    """
    if not categoria:
        return "RadarBR"
    
    # Texto mais específico por categoria
    text_map = {
        'agro': "Agro",
        'brasil': "Brasil", 
        'carros-mobilidade': "Carros",
        'cidades-rs': "Cidades",
        'ciencia-meio-ambiente': "Ciência",
        'economia': "Economia",
        'educacao': "Educação",
        'entretenimento': "Entretenimento",
        'esportes': "Esportes",
        'geral': "RadarBR",
        'justica-seguranca': "Justiça",
        'loterias': "Loterias",
        'mundo': "Mundo",
        'politica': "Política",
        'saude': "Saúde",
        'tecnologia': "Tecnologia",
        'trabalho-carreira': "Trabalho",
        'turismo': "Turismo",
    }
    
    return text_map.get(categoria.slug, "RadarBR")
