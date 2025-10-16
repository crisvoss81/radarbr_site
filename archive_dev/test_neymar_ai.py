#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from rb_ingestor.ai_enhanced import generate_enhanced_article

# Testar com notícia específica sobre Neymar
news = {
    'title': 'Grávida, garota de programa ligada a Neymar surge com exame de DNA',
    'description': 'Any Awuada faz exame de DNA da filha após escândalo com Neymar Jr.: Já têm - Terra. Acompanhante do caso Neymar comenta resultado do teste de paternidade: Dá processo - Jornal Correio',
    'source': 'Metrópoles'
}

print("=== TESTE DA IA MELHORADA - NEYMAR ===")
print(f"Tópico: Neymar")
print(f"Notícia: {news['title']}")
print(f"Descrição: {news['description']}")
print()

result = generate_enhanced_article('Neymar', news, 800)

if result:
    print("✅ SUCESSO!")
    print(f"Título: {result.get('title')}")
    print(f"Palavras: {result.get('word_count')}")
    print(f"Qualidade: {result.get('quality_score')}%")
    print()
    print("Conteúdo (primeiros 1000 caracteres):")
    print(result.get('html', '')[:1000] + "...")
else:
    print("❌ FALHOU - IA não gerou conteúdo")



