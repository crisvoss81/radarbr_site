#!/usr/bin/env python3
"""
Script simplificado para publicar artigos sem emojis (compatível com Windows)
"""

import subprocess
import sys
import time

# Lista de 15 tópicos variados para testar diferentes cenários
topics = [
    # Figuras públicas (Instagram)
    "Lula",
    "Katy Perry", 
    "Neymar",
    "Anitta",
    "Elon Musk",
    
    # Temas gerais (bancos gratuitos)
    "Energia Solar",
    "Inteligencia Artificial",
    "Mudancas Climaticas",
    "Economia Brasileira",
    "Tecnologia 5G",
    
    # Esportes (figuras públicas)
    "Cristiano Ronaldo",
    "Messi",
    
    # Política (figuras públicas)
    "Bolsonaro",
    "Marina Silva",
    
    # Celebridades (figuras públicas)
    "Taylor Swift"
]

def publish_article(topic, index):
    """Publica um artigo individual"""
    print(f"\n{'='*60}")
    print(f"ARTIGO {index+1}/15: {topic}")
    print(f"{'='*60}")
    
    try:
        # Executar comando de publicação
        result = subprocess.run([
            sys.executable, "manage.py", "publish_topic", topic, "--words", "800"
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print(f"SUCESSO: Artigo {index+1} publicado!")
            # Extrair informações importantes do output
            lines = result.stdout.split('\n')
            for line in lines:
                if any(keyword in line for keyword in ['Figura publica', 'Instagram', 'Imagem', 'Artigo publicado']):
                    print(f"   {line}")
        else:
            print(f"ERRO ao publicar artigo {index+1}:")
            print(f"   {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT ao publicar artigo {index+1}")
    except Exception as e:
        print(f"ERRO inesperado no artigo {index+1}: {e}")
    
    # Pausa entre artigos para não sobrecarregar APIs
    time.sleep(2)

def main():
    """Função principal"""
    print("INICIANDO PUBLICACAO DE 15 ARTIGOS")
    print("Testando sistema inteligente de imagens")
    print(f"Data: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    
    for i, topic in enumerate(topics):
        publish_article(topic, i)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n{'='*60}")
    print("PUBLICACAO CONCLUIDA!")
    print(f"Tempo total: {duration:.1f} segundos")
    print(f"Artigos processados: {len(topics)}")
    print(f"{'='*60}")
    
    # Verificar resultado final
    try:
        result = subprocess.run([
            sys.executable, "manage.py", "shell", "-c", 
            "from rb_noticias.models import Noticia; print(f'Total de noticias: {Noticia.objects.count()}')"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(result.stdout.strip())
    except Exception as e:
        print(f"ERRO ao verificar contagem: {e}")

if __name__ == "__main__":
    main()



