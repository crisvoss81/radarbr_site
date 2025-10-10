#!/usr/bin/env python
"""
Script simples para apagar as últimas notícias no shell do Render
Execute com: python apagar_noticias_render.py
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from rb_noticias.models import Noticia

def apagar_ultimas_noticias(num=5, confirmar=False):
    """Apaga as últimas notícias criadas"""
    print("=== APAGADOR DE NOTÍCIAS ===")
    
    # Buscar as últimas notícias
    ultimas_noticias = Noticia.objects.order_by('-criado_em')[:num]
    
    if not ultimas_noticias.exists():
        print("❌ Nenhuma notícia encontrada para apagar.")
        return
    
    # Mostrar notícias que serão apagadas
    print(f"\n📰 ÚLTIMAS {num} NOTÍCIAS QUE SERÃO APAGADAS:")
    for i, noticia in enumerate(ultimas_noticias, 1):
        print(f"{i}. {noticia.titulo}")
        print(f"   Categoria: {noticia.categoria.nome if noticia.categoria else 'Sem categoria'}")
        print(f"   Criado em: {noticia.criado_em}")
        print(f"   Slug: {noticia.slug}")
        print("")
    
    # Confirmar exclusão
    if not confirmar:
        confirmacao = input(f"\n⚠️ Tem certeza que deseja apagar estas {len(ultimas_noticias)} notícias? (s/N): ")
        if confirmacao.lower() not in ['s', 'sim', 'y', 'yes']:
            print("❌ Operação cancelada.")
            return
    
    # Apagar notícias
    apagadas = 0
    for noticia in ultimas_noticias:
        try:
            titulo = noticia.titulo
            noticia.delete()
            apagadas += 1
            print(f"✓ Apagada: {titulo}")
        except Exception as e:
            print(f"✗ Erro ao apagar '{noticia.titulo}': {e}")
    
    # Resumo final
    print(f"\n✅ CONCLUÍDO:")
    print(f"✅ Notícias apagadas: {apagadas}")
    print(f"📊 Total restante no sistema: {Noticia.objects.count()}")
    
    # Mostrar as novas últimas notícias
    if Noticia.objects.exists():
        print(f"\n📰 NOVAS ÚLTIMAS 3 NOTÍCIAS:")
        for n in Noticia.objects.order_by('-criado_em')[:3]:
            print(f"   • {n.titulo}")
    else:
        print("\n📰 Nenhuma notícia restante no sistema.")

def listar_ultimas_noticias(num=10):
    """Lista as últimas notícias sem apagar"""
    print("=== ÚLTIMAS NOTÍCIAS ===")
    
    noticias = Noticia.objects.order_by('-criado_em')[:num]
    
    if not noticias.exists():
        print("❌ Nenhuma notícia encontrada.")
        return
    
    for i, n in enumerate(noticias, 1):
        print(f"{i}. {n.titulo}")
        print(f"   Categoria: {n.categoria.nome if n.categoria else 'Sem categoria'}")
        print(f"   Criado em: {n.criado_em}")
        print(f"   Slug: {n.slug}")
        print("")

if __name__ == "__main__":
    # Verificar argumentos
    if len(sys.argv) > 1:
        comando = sys.argv[1].lower()
        
        if comando == "listar":
            num = 10
            if len(sys.argv) > 2:
                try:
                    num = int(sys.argv[2])
                except ValueError:
                    print("Uso: python apagar_noticias_render.py listar [número]")
                    sys.exit(1)
            listar_ultimas_noticias(num)
            
        elif comando == "apagar":
            num = 5
            confirmar = False
            
            if len(sys.argv) > 2:
                try:
                    num = int(sys.argv[2])
                except ValueError:
                    print("Uso: python apagar_noticias_render.py apagar [número]")
                    sys.exit(1)
            
            if len(sys.argv) > 3 and sys.argv[3].lower() == "--confirm":
                confirmar = True
            
            apagar_ultimas_noticias(num, confirmar)
            
        else:
            print("Comandos disponíveis:")
            print("  python apagar_noticias_render.py listar [número]")
            print("  python apagar_noticias_render.py apagar [número] [--confirm]")
    else:
        # Modo interativo
        print("=== APAGADOR DE NOTÍCIAS INTERATIVO ===")
        print("1. Listar últimas notícias")
        print("2. Apagar últimas notícias")
        print("3. Sair")
        
        opcao = input("\nEscolha uma opção (1-3): ")
        
        if opcao == "1":
            num = input("Quantas notícias listar? (padrão: 10): ")
            try:
                num = int(num) if num else 10
            except ValueError:
                num = 10
            listar_ultimas_noticias(num)
            
        elif opcao == "2":
            num = input("Quantas notícias apagar? (padrão: 5): ")
            try:
                num = int(num) if num else 5
            except ValueError:
                num = 5
            apagar_ultimas_noticias(num)
            
        elif opcao == "3":
            print("Saindo...")
        else:
            print("Opção inválida.")
