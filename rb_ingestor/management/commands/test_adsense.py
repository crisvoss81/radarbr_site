# rb_ingestor/management/commands/test_adsense.py
"""
Comando para testar slots do AdSense
"""
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = "Testa configuração do AdSense"

    def handle(self, *args, **options):
        self.stdout.write("=== TESTE DE CONFIGURAÇÃO ADSENSE ===")
        
        # Verificar configurações
        client_id = getattr(settings, 'ADSENSE_CLIENT', None)
        ga4_id = getattr(settings, 'GA4_ID', None)
        debug = settings.DEBUG
        
        self.stdout.write(f"ADSENSE_CLIENT: {client_id}")
        self.stdout.write(f"GA4_ID: {ga4_id}")
        self.stdout.write(f"DEBUG: {debug}")
        
        # Verificar slots usados nos templates
        slots_used = [
            "9538493649",  # Sidebar Top
            "7682486493",  # Home Inline
            "8692315830",  # Entre Cards
            "4840700734",  # Post Header
            "4286166963",  # Sidebar Middle
            "3631506847",  # Sidebar Bottom
        ]
        
        self.stdout.write("\n=== SLOTS CONFIGURADOS ===")
        for slot in slots_used:
            if slot.startswith("123456789"):
                self.stdout.write(self.style.ERROR(f"ERRO Slot invalido: {slot}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"OK Slot valido: {slot}"))
        
        # Recomendações
        self.stdout.write("\n=== RECOMENDACOES ===")
        if not client_id:
            self.stdout.write(self.style.ERROR("ERRO ADSENSE_CLIENT nao configurado"))
        else:
            self.stdout.write(self.style.SUCCESS("OK ADSENSE_CLIENT configurado"))
            
        if debug:
            self.stdout.write(self.style.WARNING("AVISO DEBUG=True - alguns recursos podem nao funcionar"))
        
        self.stdout.write("\n=== PROXIMOS PASSOS ===")
        self.stdout.write("1. Verifique se os slots sao validos no AdSense")
        self.stdout.write("2. Confirme se o site esta aprovado")
        self.stdout.write("3. Aguarde ate 48h para anuncios aparecerem")
        self.stdout.write("4. Teste em modo incognito (sem bloqueadores)")
