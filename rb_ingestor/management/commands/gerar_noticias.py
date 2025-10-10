# rb_ingestor/management/commands/gerar_noticias.py
"""
Comando simples e confiável para gerar notícias no Render
Funciona sem dependências externas problemáticas
"""
import os
import sys
import django
from django.core.management.base import BaseCommand
from django.apps import apps
from django.utils import timezone
from django.utils.html import strip_tags
from slugify import slugify
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = "Comando simples e confiável para gerar notícias"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=3, help="Número de notícias a criar")
        parser.add_argument("--force", action="store_true", help="Força criação mesmo se similar existir")
        parser.add_argument("--debug", action="store_true", help="Mostra informações detalhadas")

    def handle(self, *args, **options):
        Noticia = apps.get_model("rb_noticias", "Noticia")
        Categoria = apps.get_model("rb_noticias", "Categoria")
        
        self.stdout.write("=== GERADOR DE NOTÍCIAS SIMPLES ===")
        
        # Verificar se já existem notícias recentes
        recent_count = Noticia.objects.filter(
            criado_em__gte=timezone.now() - timedelta(hours=6)
        ).count()
        
        if not options["force"] and recent_count >= 5:
            self.stdout.write(f"⚠️ Já existem {recent_count} notícias recentes. Use --force para forçar.")
            return
        
        # Tópicos pré-definidos
        topicos = [
            "Tecnologia no Brasil",
            "Economia brasileira atual", 
            "Esportes nacionais",
            "Cultura e entretenimento",
            "Política nacional",
            "Meio ambiente",
            "Educação no Brasil",
            "Saúde pública",
            "Inovação e startups",
            "Turismo nacional",
            "Ciência e pesquisa",
            "Arte e cultura",
            "Sustentabilidade",
            "Mercado de trabalho",
            "Tendências digitais"
        ]
        
        # Criar categoria geral se não existir
        cat_geral, created = Categoria.objects.get_or_create(
            slug="geral",
            defaults={"nome": "Geral"}
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f"✓ Categoria criada: {cat_geral.nome}"))
        
        created_count = 0
        limit = options["limit"]
        
        if options["debug"]:
            self.stdout.write(f"📊 Total de notícias no sistema: {Noticia.objects.count()}")
            self.stdout.write(f"📊 Notícias recentes (6h): {recent_count}")
            self.stdout.write(f"🎯 Criando {limit} notícias...")
        
        for i in range(limit):
            # Escolher tópico aleatório
            topico = random.choice(topicos)
            
            # Gerar título único
            timestamp = timezone.now().strftime('%d/%m %H:%M')
            title = f"{topico} - {timestamp}"
            slug = slugify(title)[:180]
            
            # Verificar se já existe
            if not options["force"] and Noticia.objects.filter(slug=slug).exists():
                if options["debug"]:
                    self.stdout.write(f"⚠ Pulando: {title} (já existe)")
                continue
            
            # Gerar conteúdo simples
            conteudo = self._gerar_conteudo_simples(topico)
            
            # Criar notícia
            try:
                noticia = Noticia.objects.create(
                    titulo=title,
                    slug=slug,
                    conteudo=conteudo,
                    publicado_em=timezone.now(),
                    categoria=cat_geral,
                    fonte_url=f"gerador-simples-{timezone.now().strftime('%Y%m%d-%H%M')}-{i}",
                    fonte_nome="RadarBR Gerador",
                    status=1,  # PUBLICADO
                    imagem_alt=f"Imagem relacionada a {topico}"
                )
                
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"✓ Criado: {title}"))
                
                if options["debug"]:
                    self.stdout.write(f"   Slug: {slug}")
                    self.stdout.write(f"   Categoria: {cat_geral.nome}")
                    self.stdout.write(f"   Status: {noticia.status}")
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ Erro ao criar '{title}': {e}"))
                if options["debug"]:
                    import traceback
                    traceback.print_exc()
        
        # Resumo final
        self.stdout.write(self.style.SUCCESS(f"\n=== CONCLUÍDO ==="))
        self.stdout.write(f"✅ Notícias criadas: {created_count}")
        self.stdout.write(f"📊 Total no sistema: {Noticia.objects.count()}")
        
        # Mostrar últimas notícias criadas
        if created_count > 0:
            self.stdout.write(f"\n📰 Últimas {min(3, created_count)} notícias:")
            for n in Noticia.objects.order_by('-criado_em')[:3]:
                self.stdout.write(f"   • {n.titulo}")
        
        # Ping sitemap se criou notícias
        if created_count > 0:
            try:
                from django.core.management import call_command
                call_command('ping_sitemap')
                self.stdout.write("✓ Sitemap atualizado")
            except Exception as e:
                self.stdout.write(f"⚠ Erro ao atualizar sitemap: {e}")

    def _gerar_conteudo_simples(self, topico):
        """Gera conteúdo simples em HTML"""
        return f"""
        <div class="article-content">
            <h2>Sobre {topico}</h2>
            
            <p>Este é um artigo gerado automaticamente sobre <strong>{topico}</strong>. 
            O conteúdo aborda aspectos relevantes e atuais relacionados ao tema.</p>
            
            <h3>Principais Aspectos</h3>
            <ul>
                <li>Aspecto importante relacionado a {topico}</li>
                <li>Desenvolvimento atual no campo</li>
                <li>Impacto na sociedade brasileira</li>
            </ul>
            
            <h3>Análise</h3>
            <p>{topico} representa um tema de grande relevância no contexto atual. 
            É importante acompanhar os desenvolvimentos e tendências relacionadas 
            a este assunto para manter-se informado.</p>
            
            <h3>Conclusão</h3>
            <p>Este artigo fornece uma visão geral sobre {topico}, destacando 
            aspectos importantes e relevantes para o público brasileiro.</p>
            
            <p><em>Artigo gerado automaticamente pelo sistema RadarBR.</em></p>
        </div>
        """
