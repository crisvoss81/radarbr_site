# rb_ingestor/management/commands/apagar_noticias.py
"""
Comando para apagar as últimas notícias criadas
"""
from django.core.management.base import BaseCommand
from django.apps import apps
from django.utils import timezone

class Command(BaseCommand):
    help = "Apaga as últimas notícias criadas"

    def add_arguments(self, parser):
        parser.add_argument("--num", type=int, default=5, help="Número de notícias a apagar")
        parser.add_argument("--confirm", action="store_true", help="Confirma a exclusão sem perguntar")
        parser.add_argument("--debug", action="store_true", help="Mostra informações detalhadas")

    def handle(self, *args, **options):
        Noticia = apps.get_model("rb_noticias", "Noticia")
        
        self.stdout.write("=== APAGADOR DE NOTICIAS ===")
        
        # Buscar as últimas notícias
        num = options["num"]
        ultimas_noticias = Noticia.objects.order_by('-criado_em')[:num]
        
        if not ultimas_noticias.exists():
            self.stdout.write("ERRO: Nenhuma noticia encontrada para apagar.")
            return
        
        # Mostrar notícias que serão apagadas
        self.stdout.write(f"\nULTIMAS {num} NOTICIAS QUE SERAO APAGADAS:")
        for i, noticia in enumerate(ultimas_noticias, 1):
            self.stdout.write(f"{i}. {noticia.titulo}")
            self.stdout.write(f"   Categoria: {noticia.categoria.nome if noticia.categoria else 'Sem categoria'}")
            self.stdout.write(f"   Criado em: {noticia.criado_em}")
            self.stdout.write(f"   Slug: {noticia.slug}")
            if options["debug"]:
                self.stdout.write(f"   ID: {noticia.id}")
                self.stdout.write(f"   Status: {noticia.status}")
            self.stdout.write("")
        
        # Confirmar exclusão
        if not options["confirm"]:
            confirmacao = input(f"\nAVISO: Tem certeza que deseja apagar estas {len(ultimas_noticias)} noticias? (s/N): ")
            if confirmacao.lower() not in ['s', 'sim', 'y', 'yes']:
                self.stdout.write("ERRO: Operacao cancelada.")
                return
        
        # Apagar notícias
        apagadas = 0
        for noticia in ultimas_noticias:
            try:
                titulo = noticia.titulo
                noticia.delete()
                apagadas += 1
                self.stdout.write(f"OK Apagada: {titulo}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"ERRO ao apagar '{noticia.titulo}': {e}"))
        
        # Resumo final
        self.stdout.write(self.style.SUCCESS(f"\n=== CONCLUIDO ==="))
        self.stdout.write(f"OK Noticias apagadas: {apagadas}")
        self.stdout.write(f"Total restante no sistema: {Noticia.objects.count()}")
        
        # Mostrar as novas últimas notícias
        if Noticia.objects.exists():
            self.stdout.write(f"\nNOVAS ULTIMAS 3 NOTICIAS:")
            for n in Noticia.objects.order_by('-criado_em')[:3]:
                self.stdout.write(f"   - {n.titulo}")
        else:
            self.stdout.write("\nNenhuma noticia restante no sistema.")
