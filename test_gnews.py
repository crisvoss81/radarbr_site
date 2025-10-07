#!/usr/bin/env python3
"""
Script de teste para diagnosticar problemas com o GNews
"""
import sys
import traceback
from gnews import GNews

def test_gnews():
    print("🔍 Testando GNews...")
    
    try:
        # Teste 1: Inicialização básica
        print("\n1. Testando inicialização do GNews...")
        google_news = GNews(language='pt', country='BR', period='1d', max_results=10)
        print("✅ GNews inicializado com sucesso")
        
        # Teste 2: Busca por top news
        print("\n2. Testando busca por top news...")
        try:
            raw_articles = google_news.get_top_news()
            print(f"✅ Top news retornou {len(raw_articles)} artigos")
            
            if raw_articles:
                print("\n📰 Primeiros artigos encontrados:")
                for i, article in enumerate(raw_articles[:3]):
                    title = article.get('title', 'Sem título')
                    print(f"  {i+1}. {title}")
            else:
                print("⚠️  Nenhum artigo encontrado no top news")
                
        except Exception as e:
            print(f"❌ Erro ao buscar top news: {e}")
            traceback.print_exc()
        
        # Teste 3: Busca por termo específico
        print("\n3. Testando busca por termo específico...")
        try:
            raw_articles = google_news.get_news('notícias do Brasil')
            print(f"✅ Busca por 'notícias do Brasil' retornou {len(raw_articles)} artigos")
            
            if raw_articles:
                print("\n📰 Artigos encontrados:")
                for i, article in enumerate(raw_articles[:3]):
                    title = article.get('title', 'Sem título')
                    print(f"  {i+1}. {title}")
            else:
                print("⚠️  Nenhum artigo encontrado na busca específica")
                
        except Exception as e:
            print(f"❌ Erro ao buscar termo específico: {e}")
            traceback.print_exc()
        
        # Teste 4: Verificar estrutura dos artigos
        print("\n4. Verificando estrutura dos artigos...")
        if raw_articles:
            article = raw_articles[0]
            print("📋 Estrutura do primeiro artigo:")
            for key, value in article.items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"  {key}: {value[:100]}...")
                else:
                    print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"❌ Erro crítico no teste: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_network():
    print("\n🌐 Testando conectividade...")
    try:
        import requests
        response = requests.get('https://news.google.com', timeout=10)
        print(f"✅ Conectividade OK - Status: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Problema de conectividade: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando diagnóstico do GNews...")
    
    # Teste de conectividade
    network_ok = test_network()
    
    # Teste do GNews
    gnews_ok = test_gnews()
    
    print("\n📊 Resumo dos testes:")
    print(f"  Conectividade: {'✅ OK' if network_ok else '❌ FALHA'}")
    print(f"  GNews: {'✅ OK' if gnews_ok else '❌ FALHA'}")
    
    if not gnews_ok:
        print("\n💡 Possíveis soluções:")
        print("  1. Verificar se o GNews está atualizado: pip install --upgrade gnews")
        print("  2. Verificar conectividade com news.google.com")
        print("  3. Verificar se há bloqueios de firewall/proxy")
        print("  4. Tentar usar VPN se houver restrições geográficas")
