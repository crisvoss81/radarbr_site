#!/usr/bin/env python
"""
Script para executar automação no Render
Verifica se há poucas notícias recentes e executa automação se necessário
"""
import os
import sys
import django
from django.core.management import call_command
from django.utils import timezone
from datetime import timedelta

# Adicionar o diretório do projeto ao Python path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)

# Mudar para o diretório do projeto
os.chdir(project_dir)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from rb_noticias.models import Noticia

def main():
    print('=== VERIFICAÇÃO DE AUTOMAÇÃO RENDER ===')
    
    # Verificar notícias recentes
    total = Noticia.objects.count()
    recentes = Noticia.objects.filter(
        criado_em__gte=timezone.now() - timedelta(hours=24)
    ).count()
    
    print(f'Total notícias: {total}')
    print(f'Últimas 24h: {recentes}')
    
    # Se há poucas notícias recentes, executar automação
    if recentes < 3:
        print('⚠️ Poucas notícias recentes - executando automação...')
        
        try:
            # Executar publicação manual
            call_command('manual_publish', '--count', '3', '--strategy', 'mixed')
            print('✅ Automação executada com sucesso!')
            
        except Exception as e:
            print(f'❌ Erro na automação: {str(e)}')
            return False
            
    else:
        print('✅ Quantidade adequada de notícias recentes.')
    
    # Mostrar últimas notícias
    print('\n=== ÚLTIMAS 5 NOTÍCIAS ===')
    for n in Noticia.objects.order_by('-criado_em')[:5]:
        print(f'- {n.titulo} ({n.criado_em.strftime("%Y-%m-%d %H:%M")})')
    
    print('\n=== VERIFICAÇÃO CONCLUÍDA ===')
    return True

if __name__ == '__main__':
    main()
