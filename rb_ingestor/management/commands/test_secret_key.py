# rb_ingestor/management/commands/test_secret_key.py
"""
Comando para testar a SECRET_KEY no Render
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.signing import Signer, BadSignature
import hashlib

class Command(BaseCommand):
    help = "Testa se a SECRET_KEY está funcionando corretamente"

    def handle(self, *args, **options):
        self.stdout.write("=== TESTE DA SECRET_KEY ===")
        
        # Verificar se SECRET_KEY existe
        secret_key = settings.SECRET_KEY
        
        if not secret_key:
            self.stdout.write(self.style.ERROR("ERRO: SECRET_KEY nao configurada"))
            return
        
        # Informações básicas
        self.stdout.write(f"SECRET_KEY configurada: SIM")
        self.stdout.write(f"Tamanho da chave: {len(secret_key)} caracteres")
        self.stdout.write(f"Primeiros 10 caracteres: {secret_key[:10]}...")
        
        # Teste de assinatura
        try:
            signer = Signer()
            test_data = "teste_radarbr_2025"
            
            # Assinar dados
            signed_data = signer.sign(test_data)
            self.stdout.write(f"Dados de teste: {test_data}")
            self.stdout.write(f"Dados assinados: {signed_data}")
            
            # Verificar assinatura
            verified_data = signer.unsign(signed_data)
            self.stdout.write(f"Dados verificados: {verified_data}")
            
            if verified_data == test_data:
                self.stdout.write(self.style.SUCCESS("OK: Assinatura funcionando corretamente"))
            else:
                self.stdout.write(self.style.ERROR("ERRO: Falha na verificacao da assinatura"))
                
        except BadSignature as e:
            self.stdout.write(self.style.ERROR(f"ERRO: Assinatura invalida - {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"ERRO: Falha no teste - {e}"))
        
        # Teste de hash
        try:
            test_string = "RadarBR Test 2025"
            hash_result = hashlib.sha256((secret_key + test_string).encode()).hexdigest()
            self.stdout.write(f"Teste de hash: {hash_result[:16]}...")
            self.stdout.write(self.style.SUCCESS("OK: Hash funcionando corretamente"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"ERRO: Falha no hash - {e}"))
        
        # Verificar configurações relacionadas
        self.stdout.write("\n=== CONFIGURACOES RELACIONADAS ===")
        self.stdout.write(f"DEBUG: {settings.DEBUG}")
        self.stdout.write(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        
        # Verificar se está em produção
        if settings.DEBUG:
            self.stdout.write(self.style.WARNING("AVISO: DEBUG=True - modo desenvolvimento"))
        else:
            self.stdout.write(self.style.SUCCESS("OK: DEBUG=False - modo producao"))
        
        self.stdout.write("\n=== RESUMO ===")
        self.stdout.write("Se todos os testes passaram, sua SECRET_KEY esta funcionando!")
        self.stdout.write("Se houver erros, verifique a configuracao no Render.")
