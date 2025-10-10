# rb_ingestor/management/commands/verificar_imagens.py
"""
Comando para verificar se as imagens foram geradas corretamente
"""
from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    help = "Verifica se as imagens foram geradas nas notícias"

    def handle(self, *args, **options):
        Noticia = apps.get_model("rb_noticias", "Noticia")
        
        self.stdout.write("=== VERIFICACAO DE IMAGENS ===")
        
        # Contar notícias com e sem imagem
        total_noticias = Noticia.objects.count()
        noticias_com_imagem = Noticia.objects.exclude(imagem__isnull=True).exclude(imagem='').count()
        noticias_sem_imagem = total_noticias - noticias_com_imagem
        
        self.stdout.write(f"Total de noticias: {total_noticias}")
        self.stdout.write(f"Com imagem: {noticias_com_imagem}")
        self.stdout.write(f"Sem imagem: {noticias_sem_imagem}")
        
        # Mostrar detalhes das últimas notícias
        self.stdout.write("\n=== ULTIMAS 5 NOTICIAS ===")
        ultimas_noticias = Noticia.objects.order_by('-criado_em')[:5]
        
        for i, n in enumerate(ultimas_noticias, 1):
            self.stdout.write(f"{i}. Titulo: {n.titulo}")
            self.stdout.write(f"   Fonte: {n.fonte_nome}")
            self.stdout.write(f"   Criado: {n.criado_em.strftime('%d/%m/%Y %H:%M')}")
            
            if n.imagem:
                self.stdout.write(f"   Imagem: {n.imagem[:50]}...")
                self.stdout.write(f"   Alt: {n.imagem_alt}")
                self.stdout.write(f"   Credito: {n.imagem_credito}")
                self.stdout.write("   Status: OK")
            else:
                self.stdout.write("   Imagem: SEM IMAGEM")
                self.stdout.write("   Status: ERRO")
            
            self.stdout.write("")
        
        # Verificar problemas
        self.stdout.write("=== ANALISE DE PROBLEMAS ===")
        
        if noticias_sem_imagem > 0:
            self.stdout.write(f"AVISO: {noticias_sem_imagem} noticias sem imagem")
            
            # Mostrar quais não têm imagem
            sem_imagem = Noticia.objects.filter(imagem__isnull=True) | Noticia.objects.filter(imagem='')
            self.stdout.write("Noticias sem imagem:")
            for n in sem_imagem[:3]:
                self.stdout.write(f"  - {n.titulo} ({n.fonte_nome})")
        else:
            self.stdout.write("OK: Todas as noticias tem imagem")
        
        # Verificar se há imagens inválidas
        imagens_invalidas = 0
        for n in Noticia.objects.exclude(imagem__isnull=True).exclude(imagem=''):
            if not n.imagem.startswith('http'):
                imagens_invalidas += 1
        
        if imagens_invalidas > 0:
            self.stdout.write(f"AVISO: {imagens_invalidas} imagens com URL invalida")
        else:
            self.stdout.write("OK: Todas as imagens tem URL valida")
        
        # Resumo
        self.stdout.write(f"\n=== RESUMO ===")
        self.stdout.write(f"Taxa de sucesso: {(noticias_com_imagem/total_noticias)*100:.1f}%")
        
        if noticias_com_imagem == total_noticias:
            self.stdout.write(self.style.SUCCESS("OK: Todas as noticias tem imagem"))
        else:
            self.stdout.write(self.style.WARNING(f"AVISO: {noticias_sem_imagem} noticias sem imagem"))
