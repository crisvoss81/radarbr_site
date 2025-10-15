# rb_ingestor/management/commands/automacao_webhook.py
"""
Comando para executar automação via webhook
Pode ser chamado por schedulers externos como cron-job.org
"""
from django.core.management.base import BaseCommand
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Executa automação via webhook"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=3, help="Número máximo de artigos")
        parser.add_argument("--force", action="store_true", help="Força execução")
        parser.add_argument("--webhook-url", type=str, help="URL do webhook para chamar")

    def handle(self, *args, **options):
        # Importar e executar a automação
        from rb_ingestor.management.commands.automacao_render import Command as AutoCommand
        
        auto_cmd = AutoCommand()
        auto_cmd.stdout = self.stdout
        auto_cmd.stderr = self.stderr
        
        try:
            auto_cmd.handle(
                limit=options['limit'],
                force=options['force']
            )
            self.stdout.write("✅ Automação executada com sucesso via webhook")
        except Exception as e:
            self.stdout.write(f"❌ Erro na automação: {e}")
            raise

@csrf_exempt
@require_http_methods(["POST"])
def automacao_webhook_view(request):
    """
    View para receber webhooks de automação
    """
    try:
        # Executar automação
        from django.core.management import call_command
        call_command('automacao_render', limit=3, force=True)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Automação executada com sucesso'
        })
    except Exception as e:
        logger.error(f"Erro no webhook de automação: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
