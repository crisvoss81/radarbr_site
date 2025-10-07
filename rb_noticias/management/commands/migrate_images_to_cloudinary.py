#!/usr/bin/env python3
"""
Script para migrar imagens existentes do sistema de arquivos local para o Cloudinary
Execute: python manage.py migrate_images_to_cloudinary
"""

import os
from django.core.management.base import BaseCommand
from django.conf import settings
from rb_noticias.models import Noticia
import cloudinary
import cloudinary.uploader
from pathlib import Path

class Command(BaseCommand):
    help = 'Migra imagens existentes para o Cloudinary'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra o que seria feito sem fazer upload',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Configurar Cloudinary: aceita CLOUDINARY_URL ou chaves separadas
        cloudinary_url = os.getenv('CLOUDINARY_URL')
        if cloudinary_url:
            cloudinary.config(cloudinary_url=cloudinary_url, secure=True)
        else:
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
                api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
                api_secret=settings.CLOUDINARY_STORAGE['API_SECRET'],
                secure=settings.CLOUDINARY_STORAGE['SECURE']
            )

        self.stdout.write("🚀 Iniciando migração de imagens para Cloudinary...")
        
        # Buscar todas as notícias com imagens (URLs externas)
        noticias_com_imagem = Noticia.objects.filter(imagem__isnull=False).exclude(imagem='')
        
        total = noticias_com_imagem.count()
        self.stdout.write(f"📊 Encontradas {total} notícias com imagens")
        
        if dry_run:
            self.stdout.write("🔍 Modo dry-run ativado - nenhum upload será feito")
        
        sucessos = 0
        erros = 0
        
        for i, noticia in enumerate(noticias_com_imagem, 1):
            try:
                # Suporte a URLs externas: subir diretamente a URL para o Cloudinary
                if noticia.imagem and isinstance(noticia.imagem, str):
                    remote_url = noticia.imagem
                    self.stdout.write(f"[{i}/{total}] Enviando URL remota: {remote_url[:80]}...")

                    if not dry_run:
                        resultado = cloudinary.uploader.upload(
                            remote_url,
                            folder="radarbr/noticias",
                            public_id=f"noticia_{noticia.id}",
                            quality="auto",
                            fetch_format="auto",
                            resource_type="image",
                        )

                        noticia.imagem = resultado['secure_url']
                        noticia.save(update_fields=["imagem"])
                        self.stdout.write(f"✅ Upload concluído: {resultado['secure_url']}")
                    else:
                        self.stdout.write(f"🔍 (dry-run) Upload de URL: {remote_url[:80]}...")

                    sucessos += 1
                else:
                    self.stdout.write(f"⚠️ Notícia sem URL de imagem: {noticia.titulo[:50]}")
                    erros += 1
                    
            except Exception as e:
                self.stdout.write(f"❌ Erro ao processar {noticia.titulo[:50]}: {str(e)}")
                erros += 1
        
        # Resumo
        self.stdout.write("\n" + "="*50)
        self.stdout.write("📈 RESUMO DA MIGRAÇÃO:")
        self.stdout.write(f"✅ Sucessos: {sucessos}")
        self.stdout.write(f"❌ Erros: {erros}")
        self.stdout.write(f"📊 Total processado: {sucessos + erros}")
        
        if dry_run:
            self.stdout.write("\n🔍 Para executar a migração real, remova a flag --dry-run")
        else:
            self.stdout.write("\n🎉 Migração concluída!")
            self.stdout.write("💡 Lembre-se de configurar as variáveis CLOUDINARY_* no Render")
