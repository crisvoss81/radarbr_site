#!/usr/bin/env python
"""
Script para sincronizar Render com ambiente local
Executa automação e atualizações necessárias
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.management import call_command
from django.utils import timezone
from rb_noticias.models import Noticia, Categoria
from django.conf import settings

def log(message):
    """Função de log com timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def check_environment():
    """Verifica configurações do ambiente"""
    log("=== VERIFICANDO AMBIENTE ===")
    
    debug = settings.DEBUG
    adsense_client = getattr(settings, 'ADSENSE_CLIENT', None)
    ga4_id = getattr(settings, 'GA4_ID', None)
    
    log(f"DEBUG: {debug}")
    log(f"ADSENSE_CLIENT: {adsense_client}")
    log(f"GA4_ID: {ga4_id}")
    
    if debug:
        log("⚠️ AMBIENTE EM DEBUG - AdSense mostrará placeholders")
    else:
        log("✅ AMBIENTE EM PRODUÇÃO - AdSense funcionará normalmente")
    
    return {
        'debug': debug,
        'adsense_client': adsense_client,
        'ga4_id': ga4_id
    }

def check_news_status():
    """Verifica status das notícias"""
    log("=== VERIFICANDO NOTÍCIAS ===")
    
    total = Noticia.objects.count()
    log(f"Total de notícias: {total}")
    
    # Últimas 24h
    recentes = Noticia.objects.filter(
        criado_em__gte=timezone.now() - timedelta(hours=24)
    )
    log(f"Últimas 24h: {recentes.count()}")
    
    # Últimas 7 dias
    semana = Noticia.objects.filter(
        criado_em__gte=timezone.now() - timedelta(days=7)
    )
    log(f"Última semana: {semana.count()}")
    
    # Por categoria
    log("Por categoria:")
    for cat in Categoria.objects.all():
        count = Noticia.objects.filter(categoria=cat).count()
        log(f"  {cat.nome}: {count}")
    
    return {
        'total': total,
        'recentes_24h': recentes.count(),
        'semana': semana.count()
    }

def run_automation_if_needed(news_status):
    """Executa automação se necessário"""
    log("=== VERIFICANDO NECESSIDADE DE AUTOMAÇÃO ===")
    
    if news_status['recentes_24h'] < 3:
        log("⚠️ Poucas notícias recentes - executando automação...")
        
        try:
            # Executar automação rápida
            call_command('auto_publish', '--quick')
            log("✅ Automação rápida executada")
            
            # Verificar resultado
            novas_recentes = Noticia.objects.filter(
                criado_em__gte=timezone.now() - timedelta(hours=1)
            ).count()
            log(f"Novas notícias criadas: {novas_recentes}")
            
        except Exception as e:
            log(f"❌ Erro na automação: {str(e)}")
            return False
    else:
        log("✅ Quantidade adequada de notícias recentes")
    
    return True

def update_sitemap():
    """Atualiza sitemap"""
    log("=== ATUALIZANDO SITEMAP ===")
    
    try:
        call_command('ping_sitemap')
        log("✅ Sitemap atualizado")
    except Exception as e:
        log(f"❌ Erro ao atualizar sitemap: {str(e)}")

def clear_cache():
    """Limpa cache"""
    log("=== LIMPANDO CACHE ===")
    
    try:
        from django.core.cache import cache
        cache.clear()
        log("✅ Cache limpo")
    except Exception as e:
        log(f"❌ Erro ao limpar cache: {str(e)}")

def show_latest_news():
    """Mostra as últimas notícias"""
    log("=== ÚLTIMAS NOTÍCIAS ===")
    
    for n in Noticia.objects.order_by('-criado_em')[:5]:
        log(f"- {n.titulo}")
        log(f"  Categoria: {n.categoria.nome if n.categoria else 'Sem categoria'}")
        log(f"  Data: {n.publicado_em}")
        log(f"  Slug: {n.slug}")
        log("")

def main():
    """Função principal"""
    log("🚀 INICIANDO SINCRONIZAÇÃO RENDER")
    
    try:
        # 1. Verificar ambiente
        env_config = check_environment()
        
        # 2. Verificar notícias
        news_status = check_news_status()
        
        # 3. Executar automação se necessário
        automation_success = run_automation_if_needed(news_status)
        
        # 4. Limpar cache
        clear_cache()
        
        # 5. Atualizar sitemap
        update_sitemap()
        
        # 6. Mostrar últimas notícias
        show_latest_news()
        
        # 7. Resumo final
        log("=== RESUMO FINAL ===")
        log(f"Total notícias: {Noticia.objects.count()}")
        log(f"Últimas 24h: {news_status['recentes_24h']}")
        log(f"Ambiente: {'DEBUG' if env_config['debug'] else 'PRODUÇÃO'}")
        log(f"Automação: {'✅ Executada' if automation_success else '❌ Falhou'}")
        
        log("✅ SINCRONIZAÇÃO CONCLUÍDA COM SUCESSO")
        
    except Exception as e:
        log(f"❌ ERRO NA SINCRONIZAÇÃO: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
