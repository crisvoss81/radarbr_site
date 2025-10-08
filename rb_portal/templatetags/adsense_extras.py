# rb_portal/templatetags/adsense_extras.py
"""
Template tags para Google AdSense
"""
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def adsense_ad(ad_slot, ad_format="auto", responsive=True, width=None, height=None):
    """
    Gera código de anúncio do Google AdSense
    
    Uso:
    {% adsense_ad "1234567890" %}
    {% adsense_ad "1234567890" width=728 height=90 %}
    {% adsense_ad "1234567890" ad_format="rectangle" %}
    """
    # ID do cliente AdSense (do settings)
    client_id = settings.ADSENSE_CLIENT
    
    # Construir atributos do anúncio
    attrs = [
        f'data-ad-client="{client_id}"',
        f'data-ad-slot="{ad_slot}"'
    ]
    
    if ad_format != "auto":
        attrs.append(f'data-ad-format="{ad_format}"')
    
    if responsive:
        attrs.append('data-full-width-responsive="true"')
    
    if width and height:
        attrs.append(f'style="display:block; width:{width}px; height:{height}px;"')
    
    attrs_str = " ".join(attrs)

    html = (
        f'<ins class="adsbygoogle" {attrs_str}></ins>'
        f'<script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>'
    )
    return mark_safe(html)

@register.simple_tag
def adsense_placeholder(text="Publicidade", width=728, height=90):
    """
    Gera placeholder para anúncios durante desenvolvimento
    
    Uso:
    {% adsense_placeholder %}
    {% adsense_placeholder "Anúncio" 300 250 %}
    """
    if settings.DEBUG:
        return f'''
        <div class="ad-placeholder" style="width:{width}px; height:{height}px; background:#f3f4f6; border:2px dashed #d1d5db; border-radius:8px; display:flex; flex-direction:column; align-items:center; justify-content:center; margin:20px auto;">
            <div class="ad-label" style="font-size:0.75rem; color:#6b7280; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:8px;">{text}</div>
            <div class="ad-size" style="font-size:0.8rem; color:#3b82f6; font-weight:500;">{width}x{height}</div>
        </div>
        '''
    return ""

@register.simple_tag
def adsense_banner(ad_slot, width=728, height=90, placeholder_text="Publicidade"):
    """
    Gera banner do AdSense com fallback para placeholder em desenvolvimento
    
    Uso:
    {% adsense_banner "1234567890" %}
    {% adsense_banner "1234567890" 300 250 %}
    """
    # Sempre mostrar o anúncio real, mesmo em DEBUG
    return adsense_ad(ad_slot, width=width, height=height)
