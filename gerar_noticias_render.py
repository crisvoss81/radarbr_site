#!/usr/bin/env python
"""
Script simples para gerar notícias no shell do Render
Execute com: python gerar_noticias_render.py
"""
import os
import sys
import django
from datetime import datetime, timedelta
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.utils import timezone
from slugify import slugify
from rb_noticias.models import Noticia, Categoria

def gerar_noticias(num=3):
    """Gera notícias simples"""
    print("=== GERADOR DE NOTÍCIAS PARA RENDER ===")
    
    # Criar categoria se não existir
    cat, created = Categoria.objects.get_or_create(
        slug="geral",
        defaults={"nome": "Geral"}
    )
    
    if created:
        print(f"✓ Categoria criada: {cat.nome}")
    
    # Tópicos
    topicos = [
        "Tecnologia no Brasil",
        "Economia brasileira", 
        "Esportes nacionais",
        "Cultura brasileira",
        "Política nacional",
        "Meio ambiente",
        "Educação no Brasil",
        "Saúde pública",
        "Inovação",
        "Turismo nacional"
    ]
    
    criadas = 0
    
    for i in range(num):
        topico = random.choice(topicos)
        timestamp = timezone.now().strftime('%d/%m %H:%M')
        titulo = f"{topico} - {timestamp}"
        slug = slugify(titulo)[:180]
        
        # Verificar se já existe
        if Noticia.objects.filter(slug=slug).exists():
            print(f"⚠ Pulando: {titulo} (já existe)")
            continue
        
        # Conteúdo
        conteudo = f"""
        <div class="article">
            <h2>{topico}</h2>
            <p>Este artigo aborda aspectos importantes sobre <strong>{topico}</strong>.</p>
            
            <h3>Principais Pontos</h3>
            <ul>
                <li>Desenvolvimento atual no campo</li>
                <li>Impacto na sociedade</li>
                <li>Tendências futuras</li>
            </ul>
            
            <p>O tema {topico} é de grande relevância no contexto brasileiro atual.</p>
            
            <p><em>Artigo gerado automaticamente pelo RadarBR em {timestamp}</em></p>
        </div>
        """
        
        try:
            noticia = Noticia.objects.create(
                titulo=titulo,
                slug=slug,
                conteudo=conteudo,
                publicado_em=timezone.now(),
                categoria=cat,
                fonte_url=f"render-{timezone.now().strftime('%Y%m%d-%H%M')}-{i}",
                fonte_nome="RadarBR Render",
                status=1,
                imagem_alt=f"Imagem sobre {topico}"
            )
            
            criadas += 1
            print(f"✓ Criado: {titulo}")
            
        except Exception as e:
            print(f"✗ Erro ao criar '{titulo}': {e}")
    
    print(f"\n✅ Concluído: {criadas} notícias criadas")
    print(f"📊 Total no sistema: {Noticia.objects.count()}")
    
    # Mostrar últimas notícias
    print(f"\n📰 Últimas 3 notícias:")
    for n in Noticia.objects.order_by('-criado_em')[:3]:
        print(f"   • {n.titulo} ({n.categoria.nome if n.categoria else 'Sem categoria'})")
    
    return criadas

def verificar_status():
    """Verifica status das notícias"""
    print("=== STATUS DAS NOTÍCIAS ===")
    
    total = Noticia.objects.count()
    recentes = Noticia.objects.filter(
        criado_em__gte=timezone.now() - timedelta(hours=24)
    ).count()
    
    print(f"📊 Total de notícias: {total}")
    print(f"📊 Últimas 24h: {recentes}")
    
    if recentes < 3:
        print("⚠️ Poucas notícias recentes - recomendado gerar mais")
        return True
    else:
        print("✅ Quantidade adequada de notícias recentes")
        return False

if __name__ == "__main__":
    # Verificar argumentos
    num = 3
    if len(sys.argv) > 1:
        try:
            num = int(sys.argv[1])
        except ValueError:
            print("Uso: python gerar_noticias_render.py [número]")
            sys.exit(1)
    
    # Verificar status
    precisa_gerar = verificar_status()
    
    # Gerar notícias
    if precisa_gerar or num > 0:
        gerar_noticias(num)
    
    print("\n🎯 Para usar no shell do Render:")
    print("python gerar_noticias_render.py")
    print("python gerar_noticias_render.py 5")
