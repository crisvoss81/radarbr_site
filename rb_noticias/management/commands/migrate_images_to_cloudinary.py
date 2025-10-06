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
        
        # Configurar Cloudinary
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
            api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
            api_secret=settings.CLOUDINARY_STORAGE['API_SECRET'],
            secure=settings.CLOUDINARY_STORAGE['SECURE']
        )

        self.stdout.write("🚀 Iniciando migração de imagens para Cloudinary...")
        
        # Buscar todas as notícias com imagens
        noticias_com_imagem = Noticia.objects.filter(imagem__isnull=False).exclude(imagem='')
        
        total = noticias_com_imagem.count()
        self.stdout.write(f"📊 Encontradas {total} notícias com imagens")
        
        if dry_run:
            self.stdout.write("🔍 Modo dry-run ativado - nenhum upload será feito")
        
        sucessos = 0
        erros = 0
        
        for i, noticia in enumerate(noticias_com_imagem, 1):
            try:
                # Verificar se a imagem existe localmente
                if noticia.imagem and hasattr(noticia.imagem, 'path'):
                    caminho_local = noticia.imagem.path
                    
                    if os.path.exists(caminho_local):
                        self.stdout.write(f"[{i}/{total}] Processando: {noticia.titulo[:50]}...")
                        
                        if not dry_run:
                            # Upload para Cloudinary
                            resultado = cloudinary.uploader.upload(
                                caminho_local,
                                folder="radarbr/noticias",
                                public_id=f"noticia_{noticia.id}",
                                quality="auto",
                                format="auto",
                                transformation=[
                                    {'width': 1200, 'height': 630, 'crop': 'fill', 'quality': 'auto'},
                                    {'fetch_format': 'auto'}
                                ]
                            )
                            
                            # Atualizar o campo imagem com a URL do Cloudinary
                            noticia.imagem = resultado['secure_url']
                            noticia.save()
                            
                            self.stdout.write(f"✅ Upload concluído: {resultado['secure_url']}")
                        else:
                            self.stdout.write(f"🔍 Seria feito upload de: {caminho_local}")
                        
                        sucessos += 1
                    else:
                        self.stdout.write(f"⚠️ Arquivo não encontrado: {caminho_local}")
                        erros += 1
                else:
                    self.stdout.write(f"⚠️ Notícia sem caminho de imagem: {noticia.titulo[:50]}")
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
