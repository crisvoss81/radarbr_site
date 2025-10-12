# rb_portal/templatetags/cloudinary_extras.py
from django import template
from django.conf import settings
import cloudinary

register = template.Library()

@register.simple_tag
def cloudinary_image_url(image_field, width=None, height=None, crop='fill', quality='auto', format='auto'):
    """
    Gera URL otimizada do Cloudinary para uma imagem ou retorna URL externa
    
    Uso:
    {% cloudinary_image_url noticia.imagem width=800 height=600 %}
    {% cloudinary_image_url noticia.imagem width=400 crop='scale' %}
    """
    if not image_field:
        return ''
    
    # Converter para string se necessário
    image_url = str(image_field)
    
    # Se já é uma URL do Cloudinary, usar diretamente
    if 'cloudinary.com' in image_url:
        url = image_url
        
        # Adicionar transformações se especificadas
        if width or height or crop != 'fill' or quality != 'auto' or format != 'auto':
            transformations = []
            
            if width and height:
                transformations.append(f"w_{width},h_{height},c_{crop}")
            elif width:
                transformations.append(f"w_{width},c_{crop}")
            elif height:
                transformations.append(f"h_{height},c_{crop}")
            
            if quality != 'auto':
                transformations.append(f"q_{quality}")
            
            if format != 'auto':
                transformations.append(f"f_{format}")
            
            if transformations:
                # Inserir transformações na URL
                if '/upload/' in url:
                    url = url.replace('/upload/', f'/upload/{",".join(transformations)}/')
        
        return url
    
    # Se é uma URL externa (Unsplash, etc.), retornar diretamente
    if image_url.startswith('http'):
        return image_url
    
    # Se é um campo de arquivo, usar .url
    if hasattr(image_field, 'url'):
        return image_field.url
    
    # Fallback: retornar como string
    return image_url

@register.simple_tag
def cloudinary_responsive_image(image_field, sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"):
    """
    Gera srcset responsivo para imagens do Cloudinary ou retorna srcset simples para URLs externas
    
    Uso:
    {% cloudinary_responsive_image noticia.imagem %}
    """
    if not image_field:
        return ''
    
    base_url = cloudinary_image_url(image_field)
    
    if not base_url:
        return ''
    
    # Se não é Cloudinary (URL externa), não retornar srcset
    if 'cloudinary.com' not in base_url:
        return ''
    
    # Gerar diferentes tamanhos para Cloudinary
    sizes_list = [400, 600, 800, 1200, 1600]
    srcset_parts = []
    
    for size in sizes_list:
        if '/upload/' in base_url:
            responsive_url = base_url.replace('/upload/', f'/upload/w_{size},c_scale,q_auto,f_auto/')
            srcset_parts.append(f"{responsive_url} {size}w")
    
    srcset = ", ".join(srcset_parts)
    return f'srcset=\'{srcset}\' sizes=\'{sizes}\''

@register.simple_tag
def cloudinary_placeholder(width=400, height=300, text="RadarBR"):
    """
    Gera URL de placeholder do Cloudinary
    
    Uso:
    {% cloudinary_placeholder width=800 height=600 text="Carregando..." %}
    """
    try:
        # Configurar Cloudinary se as variáveis estiverem disponíveis
        if hasattr(settings, 'CLOUDINARY_CLOUD_NAME') and settings.CLOUDINARY_CLOUD_NAME:
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET,
            )
            
            # Gerar URL de placeholder
            url = cloudinary.utils.cloudinary_url(
                f"sample.jpg",
                width=width,
                height=height,
                crop="fill",
                quality="auto",
                format="auto",
                effect="blur:300",
                overlay=f"text:Arial_24:{text}",
                gravity="center",
                color="white"
            )[0]
            
            return url
        else:
            # Fallback se Cloudinary não estiver configurado
            raise Exception("Cloudinary not configured")
            
    except:
        # Fallback para placeholder simples
        return f"data:image/svg+xml;base64,PHN2ZyB3aWR0aD0i{width}IiBoZWlnaHQ9I{height}IiB2aWV3Qm94PSIwIDAg{width}IHtoZWlnaHR9IiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxyZWN0IHdpZHRoPSI{width}IiBoZWlnaHQ9I{height}IiBmaWxsPSIjZjNmNGY2Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzZjNzI4MCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPnt0ZXh0fTwvdGV4dD48L3N2Zz4="
