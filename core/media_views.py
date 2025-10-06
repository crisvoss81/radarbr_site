# core/media_views.py
from django.http import HttpResponse, Http404
from django.conf import settings
from django.views.decorators.cache import cache_control
from django.views.decorators.http import etag
import os
import mimetypes
import hashlib

def get_file_etag(file_path):
    """Gera ETag baseado no tamanho e modificação do arquivo"""
    try:
        stat = os.stat(file_path)
        return hashlib.md5(f"{stat.st_mtime}-{stat.st_size}".encode()).hexdigest()
    except OSError:
        return None

@cache_control(max_age=3600)  # Cache por 1 hora
@etag(get_file_etag)
def serve_media_file(request, path):
    """
    Serve arquivos de mídia com cache e headers apropriados
    """
    # Construir o caminho completo do arquivo
    full_path = os.path.join(settings.MEDIA_ROOT, path)
    
    # Verificar se o arquivo existe e está dentro do MEDIA_ROOT
    if not os.path.exists(full_path) or not full_path.startswith(settings.MEDIA_ROOT):
        raise Http404("Arquivo não encontrado")
    
    # Determinar o tipo MIME
    content_type, _ = mimetypes.guess_type(full_path)
    if content_type is None:
        content_type = 'application/octet-stream'
    
    # Ler o arquivo
    try:
        with open(full_path, 'rb') as f:
            content = f.read()
    except IOError:
        raise Http404("Erro ao ler arquivo")
    
    # Criar resposta com headers apropriados
    response = HttpResponse(content, content_type=content_type)
    response['Content-Length'] = len(content)
    
    # Headers para cache
    response['Cache-Control'] = 'public, max-age=3600'
    
    return response
