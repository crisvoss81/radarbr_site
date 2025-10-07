# test_image_search.py
"""
Script de teste para o sistema de busca de imagens.
Testa as funcionalidades principais sem depender de APIs externas.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from rb_ingestor.image_search import ImageSearchEngine, find_image_for_news
from rb_ingestor.image_cache import image_cache

def test_keyword_extraction():
    """Testa extração de palavras-chave."""
    print("🔍 Testando extração de palavras-chave...")
    
    engine = ImageSearchEngine()
    
    test_cases = [
        {
            'title': 'Nova tecnologia de inteligência artificial revoluciona mercado',
            'content': 'A inteligência artificial está transformando diversos setores da economia brasileira.',
            'expected': ['tecnologia', 'inteligência', 'artificial', 'revoluciona', 'mercado']
        },
        {
            'title': 'Chuvas intensas causam alagamentos em São Paulo',
            'content': 'As chuvas de verão estão causando problemas na capital paulista.',
            'expected': ['chuvas', 'intensas', 'causam', 'alagamentos', 'paulo']
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        keywords = engine.extract_keywords(case['title'], case['content'])
        print(f"  Teste {i}: {case['title'][:40]}...")
        print(f"    Palavras-chave: {keywords}")
        print(f"    Esperado: {case['expected']}")
        print()

def test_cache_system():
    """Testa sistema de cache."""
    print("💾 Testando sistema de cache...")
    
    # Limpar cache para teste
    image_cache.cache_data.clear()
    image_cache._save_cache()
    
    # Testar armazenamento
    test_title = "Teste de cache"
    test_url = "https://example.com/test.jpg"
    test_category = "tecnologia"
    
    image_cache.set(test_title, test_url, test_category, {'test': True})
    print(f"  ✓ Armazenado: {test_title}")
    
    # Testar recuperação
    retrieved_url = image_cache.get(test_title, test_category)
    if retrieved_url == test_url:
        print(f"  ✓ Recuperado: {retrieved_url}")
    else:
        print(f"  ✗ Erro na recuperação: {retrieved_url}")
    
    # Testar estatísticas
    stats = image_cache.get_stats()
    print(f"  ✓ Estatísticas: {stats['total_entries']} entradas")
    
    # Limpar após teste
    image_cache.cache_data.clear()
    image_cache._save_cache()

def test_image_validation():
    """Testa validação de URLs."""
    print("🔗 Testando validação de URLs...")
    
    engine = ImageSearchEngine()
    
    test_urls = [
        "https://httpbin.org/status/200",  # URL válida
        "https://httpbin.org/status/404",  # URL inválida
        "https://example.com/nonexistent", # URL inexistente
    ]
    
    for url in test_urls:
        is_valid = engine.validate_image_url(url)
        status = "✓" if is_valid else "✗"
        print(f"  {status} {url}: {'Válida' if is_valid else 'Inválida'}")

def test_category_mapping():
    """Testa mapeamento de categorias."""
    print("📂 Testando mapeamento de categorias...")
    
    engine = ImageSearchEngine()
    
    categories = [
        'agro', 'brasil', 'tecnologia', 'esportes', 'politica'
    ]
    
    for category in categories:
        image_url = engine.get_category_image(category)
        if image_url:
            print(f"  ✓ {category}: {image_url[:50]}...")
        else:
            print(f"  ✗ {category}: Nenhuma imagem encontrada")

def test_integration():
    """Testa integração completa."""
    print("🔧 Testando integração completa...")
    
    test_cases = [
        {
            'title': 'Inteligência artificial no Brasil',
            'content': 'A IA está crescendo rapidamente no mercado brasileiro.',
            'category': 'tecnologia'
        },
        {
            'title': 'Futebol brasileiro em alta',
            'content': 'O futebol nacional está passando por um bom momento.',
            'category': 'esportes'
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"  Teste {i}: {case['title']}")
        
        # Testar função principal
        image_url = find_image_for_news(
            case['title'], 
            case['content'], 
            case['category']
        )
        
        if image_url:
            print(f"    ✓ Imagem encontrada: {image_url[:60]}...")
        else:
            print(f"    ⚠ Nenhuma imagem encontrada (normal sem APIs configuradas)")

def main():
    """Executa todos os testes."""
    print("🚀 Iniciando testes do sistema de busca de imagens")
    print("=" * 60)
    
    try:
        test_keyword_extraction()
        test_cache_system()
        test_image_validation()
        test_category_mapping()
        test_integration()
        
        print("=" * 60)
        print("✅ Todos os testes concluídos!")
        print()
        print("📝 Próximos passos:")
        print("  1. Configure as APIs no arquivo .env")
        print("  2. Execute: python manage.py find_images_for_news --limit 5")
        print("  3. Verifique: python manage.py manage_image_cache --stats")
        
    except Exception as e:
        print(f"❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
