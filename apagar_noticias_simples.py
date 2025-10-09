#!/usr/bin/env python
"""
Script para apagar notícias no Render
Execute diretamente: python apagar_noticias_simples.py
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from rb_noticias.models import Noticia

def apagar_ultimas_noticias(num=5):
    """Apaga as últimas notícias criadas"""
    print("=== APAGADOR DE NOTÍCIAS SIMPLES ===")
    
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
        print("")
    
    # Confirmar exclusão
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
        print("")

if __name__ == "__main__":
    print("=== APAGADOR DE NOTÍCIAS ===")
    print("1. Listar últimas notícias")
    print("2. Apagar últimas 5 notícias")
    print("3. Apagar últimas 3 notícias")
    print("4. Apagar última notícia")
    print("5. Sair")
    
    opcao = input("\nEscolha uma opção (1-5): ")
    
    if opcao == "1":
        num = input("Quantas notícias listar? (padrão: 10): ")
        try:
            num = int(num) if num else 10
        except ValueError:
            num = 10
        listar_ultimas_noticias(num)
        
    elif opcao == "2":
        apagar_ultimas_noticias(5)
        
    elif opcao == "3":
        apagar_ultimas_noticias(3)
        
    elif opcao == "4":
        apagar_ultimas_noticias(1)
        
    elif opcao == "5":
        print("Saindo...")
    else:
        print("Opção inválida.")
