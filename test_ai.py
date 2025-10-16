#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from rb_ingestor.ai_enhanced import generate_enhanced_article

# Testar com notícia específica
news = {
    'title': 'No Iêmen, Anitta posa de biquíni e mostra trilha por gigante duna de areia',
    'description': 'Cantora compartilha momentos de sua viagem ao Iémen, posando em meio a paisagens deslumbrantes.',
    'source': 'G1'
}

print("=== TESTE DA IA MELHORADA ===")
print(f"Tópico: Anitta")
print(f"Notícia: {news['title']}")
print(f"Descrição: {news['description']}")
print()

result = generate_enhanced_article('Anitta', news, 800)

if result:
    print("✅ SUCESSO!")
    print(f"Título: {result.get('title')}")
    print(f"Palavras: {result.get('word_count')}")
    print(f"Qualidade: {result.get('quality_score')}%")
    print()
    print("Conteúdo (primeiros 500 caracteres):")
    print(result.get('html', '')[:500] + "...")
else:
    print("❌ FALHOU - IA não gerou conteúdo")



