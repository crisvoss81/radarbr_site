#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re

def extract_images_from_url(url):
    """Extrai imagens de uma URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Procurar por todas as imagens
        images = soup.find_all('img')
        
        print(f'🔍 Total de imagens encontradas: {len(images)}')
        print()
        
        # Filtrar imagens principais (não logos/ícones)
        main_images = []
        for img in images:
            src = img.get('src', '')
            alt = img.get('alt', '')
            
            # Pular logos, ícones e imagens pequenas
            if src and not any(skip in src.lower() for skip in ['logo', 'icon', 'sprite', 'button', 'arrow', 'social']):
                # Verificar se é uma imagem de conteúdo
                if any(keyword in alt.lower() for keyword in ['barroso', 'stf', 'supremo', 'tribunal', 'ministro']) or len(src) > 50:
                    main_images.append((src, alt))
        
        print('📸 Imagens principais encontradas:')
        for i, (src, alt) in enumerate(main_images, 1):
            print(f'{i}. {alt}')
            print(f'   URL: {src}')
            print()
        
        if not main_images:
            print('⚠️ Nenhuma imagem principal encontrada automaticamente')
            print('📋 Todas as imagens encontradas:')
            for i, img in enumerate(images[:5], 1):  # Mostrar apenas as primeiras 5
                src = img.get('src', '')
                alt = img.get('alt', '')
                print(f'{i}. {alt}')
                print(f'   URL: {src}')
                print()
                
        return main_images
            
    except Exception as e:
        print(f'❌ Erro: {e}')
        return []

if __name__ == "__main__":
    url = 'https://agenciabrasil.ebc.com.br/justica/noticia/2025-10/barroso-pede-retomada-do-julgamento-sobre-descriminalizacao-do-aborto'
    extract_images_from_url(url)
