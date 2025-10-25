# rb_noticias/api_views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
import json
from .models import Noticia

@csrf_exempt
@require_POST
def increment_shares(request):
    """API endpoint para incrementar compartilhamentos"""
    try:
        data = json.loads(request.body)
        noticia_id = data.get('noticia_id')
        
        if not noticia_id:
            return JsonResponse({'error': 'ID da notícia é obrigatório'}, status=400)
        
        try:
            noticia = Noticia.objects.get(id=noticia_id)
            noticia.increment_shares()
            
            return JsonResponse({
                'success': True,
                'shares': noticia.shares,
                'trending_score': noticia.trending_score
            })
            
        except Noticia.DoesNotExist:
            return JsonResponse({'error': 'Notícia não encontrada'}, status=404)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Erro interno: {str(e)}'}, status=500)
