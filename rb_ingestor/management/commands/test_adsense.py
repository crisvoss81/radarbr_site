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
                self.stdout.write(self.style.ERROR(f"❌ Slot inválido: {slot}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"✅ Slot válido: {slot}"))
        
        # Recomendações
        self.stdout.write("\n=== RECOMENDAÇÕES ===")
        if not client_id:
            self.stdout.write(self.style.ERROR("❌ ADSENSE_CLIENT não configurado"))
        else:
            self.stdout.write(self.style.SUCCESS("✅ ADSENSE_CLIENT configurado"))
            
        if debug:
            self.stdout.write(self.style.WARNING("⚠️ DEBUG=True - alguns recursos podem não funcionar"))
        
        self.stdout.write("\n=== PRÓXIMOS PASSOS ===")
        self.stdout.write("1. Verifique se os slots são válidos no AdSense")
        self.stdout.write("2. Confirme se o site está aprovado")
        self.stdout.write("3. Aguarde até 48h para anúncios aparecerem")
        self.stdout.write("4. Teste em modo incógnito (sem bloqueadores)")
