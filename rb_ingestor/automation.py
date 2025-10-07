#!/usr/bin/env python
"""
Script de automação para publicação inteligente de notícias
Executa diferentes estratégias baseadas no horário e dia da semana
"""
import os
import sys
import django
from datetime import datetime, timedelta
import logging

# Configurar logging
import os
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'automation.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.management import call_command
from django.utils import timezone
from rb_noticias.models import Noticia
from rb_ingestor.audience_analyzer import AudienceAnalyzer

class NewsAutomation:
    def __init__(self):
        self.analyzer = AudienceAnalyzer()
        self.logger = logger
    
    def get_strategy_for_time(self):
        """Determina a estratégia baseada no horário atual"""
        now = timezone.now()
        hour = now.hour
        weekday = now.weekday()  # 0 = segunda, 6 = domingo
        
        # Estratégias baseadas no horário
        if 6 <= hour < 12:  # Manhã
            return "trending", 3  # Trending topics, 3 artigos
        elif 12 <= hour < 18:  # Tarde
            return "audience", 4  # Baseado na audiência, 4 artigos
        elif 18 <= hour < 22:  # Noite (horário de pico)
            return "mixed", 5  # Estratégia mista, 5 artigos
        else:  # Madrugada
            return "trending", 2  # Trending topics, 2 artigos
    
    def should_include_seasonal(self):
        """Determina se deve incluir tópicos sazonais"""
        now = timezone.now()
        
        # Incluir sazonais em datas especiais
        special_dates = [
            (1, 1),   # Ano Novo
            (2, 14),  # Dia dos Namorados
            (4, 21),  # Tiradentes
            (5, 1),   # Dia do Trabalho
            (5, 12),  # Dia das Mães
            (6, 12),  # Dia dos Namorados (Brasil)
            (8, 11),  # Dia dos Pais
            (9, 7),   # Independência
            (10, 12), # Dia das Crianças
            (11, 15), # Proclamação da República
            (12, 25), # Natal
        ]
        
        current_date = (now.month, now.day)
        return current_date in special_dates
    
    def check_recent_publications(self, hours=6):
        """Verifica se já houve publicações recentes"""
        cutoff_time = timezone.now() - timedelta(hours=hours)
        recent_count = Noticia.objects.filter(
            criado_em__gte=cutoff_time
        ).count()
        
        return recent_count
    
    def run_automation(self):
        """Executa a automação principal"""
        try:
            self.logger.info("=== INICIANDO AUTOMAÇÃO DE NOTÍCIAS ===")
            
            # Verificar se já houve publicações recentes
            recent_count = self.check_recent_publications(6)
            if recent_count >= 5:
                self.logger.info(f"Já existem {recent_count} notícias recentes. Pulando execução.")
                return
            
            # Determinar estratégia
            strategy, limit = self.get_strategy_for_time()
            include_seasonal = self.should_include_seasonal()
            
            self.logger.info(f"Estratégia: {strategy}, Limite: {limit}, Sazonal: {include_seasonal}")
            
            # Preparar argumentos do comando
            command_args = [
                'smart_trends_publish',
                '--strategy', strategy,
                '--limit', str(limit),
                '--force'  # Força publicação mesmo se similar existir
            ]
            
            if include_seasonal:
                command_args.append('--include-seasonal')
            
            # Executar comando
            self.logger.info(f"Executando: python manage.py {' '.join(command_args)}")
            
            call_command(*command_args)
            
            # Verificar resultados
            total_news = Noticia.objects.count()
            self.logger.info(f"Total de notícias no sistema: {total_news}")
            
            # Análise de performance
            insights = self.analyzer.get_audience_insights()
            self.logger.info(f"Top categorias: {insights['top_categories']}")
            self.logger.info(f"Palavras-chave trending: {insights['trending_keywords'][:3]}")
            
            self.logger.info("=== AUTOMAÇÃO CONCLUÍDA COM SUCESSO ===")
            
        except Exception as e:
            self.logger.error(f"Erro na automação: {str(e)}")
            raise
    
    def run_quick_update(self):
        """Execução rápida para testes"""
        try:
            self.logger.info("=== EXECUÇÃO RÁPIDA ===")
            
            call_command(
                'smart_trends_publish',
                '--strategy', 'mixed',
                '--limit', '2',
                '--force'
            )
            
            self.logger.info("=== EXECUÇÃO RÁPIDA CONCLUÍDA ===")
            
        except Exception as e:
            self.logger.error(f"Erro na execução rápida: {str(e)}")
            raise

def main():
    """Função principal"""
    automation = NewsAutomation()
    
    # Verificar argumentos da linha de comando
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        automation.run_quick_update()
    else:
        automation.run_automation()

if __name__ == '__main__':
    main()
