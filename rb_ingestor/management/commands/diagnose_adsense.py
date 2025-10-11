# rb_ingestor/management/commands/diagnose_adsense.py
"""
Comando para diagnosticar problemas do AdSense
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django.template.loader import render_to_string
from django.template import Context, Template
import requests

class Command(BaseCommand):
    help = "Diagnostica problemas do AdSense"

    def handle(self, *args, **options):
        self.stdout.write("=== DIAGNÓSTICO ADSENSE ===")
        
        # 1. Verificar configurações
        self._check_settings()
        
        # 2. Verificar slots
        self._check_slots()
        
        # 3. Verificar templates
        self._check_templates()
        
        # 4. Verificar conectividade
        self._check_connectivity()
        
        # 5. Verificar site em produção
        self._check_production_site()

    def _check_settings(self):
        self.stdout.write("\n📋 CONFIGURAÇÕES:")
        
        adsense_client = getattr(settings, 'ADSENSE_CLIENT', 'NÃO CONFIGURADO')
        debug = getattr(settings, 'DEBUG', False)
        ga4_id = getattr(settings, 'GA4_ID', 'NÃO CONFIGURADO')
        
        self.stdout.write(f"ADSENSE_CLIENT: {adsense_client}")
        self.stdout.write(f"DEBUG: {debug}")
        self.stdout.write(f"GA4_ID: {ga4_id}")
        
        if debug:
            self.stdout.write("⚠️  DEBUG=True - AdSense pode não funcionar localmente")
        
        if adsense_client == 'NÃO CONFIGURADO':
            self.stdout.write("❌ ADSENSE_CLIENT não configurado")
        else:
            self.stdout.write("✅ ADSENSE_CLIENT configurado")

    def _check_slots(self):
        self.stdout.write("\n🎯 SLOTS CONFIGURADOS:")
        
        # Slots encontrados nos templates
        slots = [
            "7682486493",  # Home inline
            "8692315830",  # Home between cards
            "4840700734",  # Post banners
            "9538493649",  # Sidebar top
            "4286166963",  # Sidebar middle
            "3631506847",  # Sidebar bottom
        ]
        
        for slot in slots:
            if slot.startswith("123456789"):
                self.stdout.write(f"❌ Slot inválido: {slot}")
            else:
                self.stdout.write(f"✅ Slot válido: {slot}")

    def _check_templates(self):
        self.stdout.write("\n📄 VERIFICAÇÃO DE TEMPLATES:")
        
        try:
            # Verificar se o template tag está funcionando
            from rb_portal.templatetags.adsense_extras import adsense_banner_auto
            
            # Testar geração de anúncio
            result = adsense_banner_auto("7682486493")
            
            if "adsbygoogle" in str(result):
                self.stdout.write("✅ Template tag funcionando")
            else:
                self.stdout.write("⚠️  Template tag retornando placeholder")
                
        except Exception as e:
            self.stdout.write(f"❌ Erro no template tag: {e}")

    def _check_connectivity(self):
        self.stdout.write("\n🌐 CONECTIVIDADE:")
        
        try:
            # Testar conexão com Google AdSense
            response = requests.get("https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js", timeout=10)
            
            if response.status_code == 200:
                self.stdout.write("✅ Conectividade com Google AdSense OK")
            else:
                self.stdout.write(f"⚠️  Status HTTP: {response.status_code}")
                
        except Exception as e:
            self.stdout.write(f"❌ Erro de conectividade: {e}")

    def _check_production_site(self):
        self.stdout.write("\n🚀 SITE EM PRODUÇÃO:")
        
        site_url = getattr(settings, 'SITE_BASE_URL', 'https://www.radarbr.com')
        
        try:
            response = requests.get(site_url, timeout=10)
            
            if response.status_code == 200:
                self.stdout.write(f"✅ Site acessível: {site_url}")
                
                # Verificar se AdSense está no HTML
                if "adsbygoogle" in response.text:
                    self.stdout.write("✅ Código AdSense encontrado no HTML")
                else:
                    self.stdout.write("⚠️  Código AdSense não encontrado no HTML")
                    
                # Verificar se há erros de console
                if "adsbygoogle" in response.text and "adsbygoogle = window.adsbygoogle || []" in response.text:
                    self.stdout.write("✅ Script AdSense carregado corretamente")
                else:
                    self.stdout.write("⚠️  Script AdSense pode não estar carregando")
                    
            else:
                self.stdout.write(f"⚠️  Status HTTP: {response.status_code}")
                
        except Exception as e:
            self.stdout.write(f"❌ Erro ao acessar site: {e}")

    def _check_adsense_approval(self):
        self.stdout.write("\n✅ APROVAÇÃO DO ADSENSE:")
        
        self.stdout.write("Para verificar se o site está aprovado:")
        self.stdout.write("1. Acesse https://www.google.com/adsense/")
        self.stdout.write("2. Vá em 'Sites'")
        self.stdout.write("3. Verifique se radarbr.com está aprovado")
        self.stdout.write("4. Aguarde até 48h após aprovação para anúncios aparecerem")

    def _check_ad_blockers(self):
        self.stdout.write("\n🚫 BLOQUEADORES DE ANÚNCIOS:")
        
        self.stdout.write("Possíveis causas dos anúncios não aparecerem:")
        self.stdout.write("1. uBlock Origin")
        self.stdout.write("2. AdBlock Plus")
        self.stdout.write("3. AdGuard")
        self.stdout.write("4. Bloqueador nativo do navegador")
        self.stdout.write("5. Extensões de privacidade")
        
        self.stdout.write("\nPara testar:")
        self.stdout.write("1. Abra o site em modo incógnito")
        self.stdout.write("2. Desative todas as extensões")
        self.stdout.write("3. Teste em navegador diferente")
