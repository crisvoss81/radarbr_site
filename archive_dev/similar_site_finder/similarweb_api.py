# Integração com SimilarWeb API

import requests
import time
import logging
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import json

logger = logging.getLogger(__name__)

class SimilarWebAPI:
    """Classe para integração com a API do SimilarWeb"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.similarweb.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SimilarSiteFinder/1.0',
            'Accept': 'application/json'
        })
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 1 segundo entre requisições
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Faz uma requisição para a API com rate limiting"""
        try:
            # Rate limiting
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.min_request_interval:
                time.sleep(self.min_request_interval - time_since_last)
            
            # Preparar parâmetros
            if params is None:
                params = {}
            params['api_key'] = self.api_key
            
            # Fazer requisição
            url = f"{self.base_url}/{endpoint}"
            logger.info(f"Fazendo requisição para: {url}")
            
            response = self.session.get(url, params=params, timeout=30)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                logger.warning("Rate limit atingido, aguardando...")
                time.sleep(60)  # Aguardar 1 minuto
                return self._make_request(endpoint, params)
            else:
                logger.error(f"Erro na API SimilarWeb: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição: {e}")
            return None
    
    def get_similar_sites(self, domain: str, country: str = "BR", limit: int = 50) -> List[Dict]:
        """
        Busca sites similares ao domínio fornecido
        
        Args:
            domain: Domínio de referência (ex: 'exemplo.com.br')
            country: Código do país (ex: 'BR', 'US')
            limit: Número máximo de resultados
            
        Returns:
            Lista de sites similares com métricas
        """
        try:
            # Limpar domínio
            clean_domain = self._clean_domain(domain)
            if not clean_domain:
                logger.error(f"Domínio inválido: {domain}")
                return []
            
            logger.info(f"Buscando sites similares para: {clean_domain}")
            
            # Endpoint para sites similares
            endpoint = f"website/{clean_domain}/similar-sites"
            params = {
                'country': country,
                'limit': min(limit, 100)  # SimilarWeb limita a 100
            }
            
            data = self._make_request(endpoint, params)
            if not data:
                return []
            
            # Processar resultados
            similar_sites = []
            sites_data = data.get('similar_sites', [])
            
            for site_info in sites_data:
                try:
                    site_domain = site_info.get('domain', '')
                    if not site_domain:
                        continue
                    
                    # Obter métricas detalhadas do site
                    metrics = self.get_site_metrics(site_domain, country)
                    
                    similar_site = {
                        'domain': site_domain,
                        'url': f"https://{site_domain}",
                        'title': site_info.get('title', ''),
                        'description': site_info.get('description', ''),
                        'category': site_info.get('category', ''),
                        'country': country,
                        'similarity_score': site_info.get('similarity_score', 0.0),
                        **metrics
                    }
                    
                    similar_sites.append(similar_site)
                    
                except Exception as e:
                    logger.error(f"Erro ao processar site {site_info}: {e}")
                    continue
            
            logger.info(f"Encontrados {len(similar_sites)} sites similares")
            return similar_sites
            
        except Exception as e:
            logger.error(f"Erro ao buscar sites similares: {e}")
            return []
    
    def get_site_metrics(self, domain: str, country: str = "BR") -> Dict:
        """
        Obtém métricas detalhadas de um site
        
        Args:
            domain: Domínio do site
            country: Código do país
            
        Returns:
            Dicionário com métricas do site
        """
        try:
            clean_domain = self._clean_domain(domain)
            if not clean_domain:
                return {}
            
            metrics = {}
            
            # Métricas de tráfego
            traffic_endpoint = f"website/{clean_domain}/total-traffic-and-engagement/visits"
            traffic_params = {
                'country': country,
                'start_date': '2024-01-01',
                'end_date': '2024-12-31',
                'granularity': 'monthly'
            }
            
            traffic_data = self._make_request(traffic_endpoint, traffic_params)
            if traffic_data:
                visits_data = traffic_data.get('visits', [])
                if visits_data:
                    # Pegar o último mês disponível
                    latest_month = visits_data[-1]
                    metrics['monthly_visits'] = latest_month.get('visits', 0)
            
            # Métricas de engajamento
            engagement_endpoint = f"website/{clean_domain}/total-traffic-and-engagement/engagement"
            engagement_params = {
                'country': country,
                'start_date': '2024-01-01',
                'end_date': '2024-12-31',
                'granularity': 'monthly'
            }
            
            engagement_data = self._make_request(engagement_endpoint, engagement_params)
            if engagement_data:
                engagement_metrics = engagement_data.get('engagement', [])
                if engagement_metrics:
                    latest_engagement = engagement_metrics[-1]
                    metrics['bounce_rate'] = latest_engagement.get('bounce_rate', 0.0)
                    metrics['pages_per_visit'] = latest_engagement.get('pages_per_visit', 0.0)
                    metrics['avg_visit_duration'] = latest_engagement.get('avg_visit_duration', 0.0)
            
            # Ranking de tráfego
            ranking_endpoint = f"website/{clean_domain}/rankings/rank"
            ranking_params = {'country': country}
            
            ranking_data = self._make_request(ranking_endpoint, ranking_params)
            if ranking_data:
                metrics['traffic_rank'] = ranking_data.get('rank', 0)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erro ao obter métricas para {domain}: {e}")
            return {}
    
    def get_site_info(self, domain: str, country: str = "BR") -> Optional[Dict]:
        """
        Obtém informações básicas de um site
        
        Args:
            domain: Domínio do site
            country: Código do país
            
        Returns:
            Dicionário com informações do site
        """
        try:
            clean_domain = self._clean_domain(domain)
            if not clean_domain:
                return None
            
            endpoint = f"website/{clean_domain}/general-data/overview"
            params = {'country': country}
            
            data = self._make_request(endpoint, params)
            if data:
                return {
                    'domain': clean_domain,
                    'title': data.get('title', ''),
                    'description': data.get('description', ''),
                    'category': data.get('category', ''),
                    'country': country,
                    'is_active': data.get('is_active', True)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter informações do site {domain}: {e}")
            return None
    
    def search_by_category(self, category: str, country: str = "BR", limit: int = 50) -> List[Dict]:
        """
        Busca sites por categoria
        
        Args:
            category: Categoria dos sites
            country: Código do país
            limit: Número máximo de resultados
            
        Returns:
            Lista de sites da categoria
        """
        try:
            logger.info(f"Buscando sites da categoria: {category}")
            
            # SimilarWeb não tem endpoint direto para busca por categoria
            # Vamos usar uma abordagem alternativa buscando sites populares
            endpoint = "website/global/rankings/rank"
            params = {
                'country': country,
                'limit': min(limit, 100)
            }
            
            data = self._make_request(endpoint, params)
            if not data:
                return []
            
            # Filtrar por categoria se possível
            sites = []
            rankings = data.get('rankings', [])
            
            for ranking in rankings:
                domain = ranking.get('domain', '')
                if domain:
                    site_info = self.get_site_info(domain, country)
                    if site_info and category.lower() in site_info.get('category', '').lower():
                        sites.append(site_info)
            
            logger.info(f"Encontrados {len(sites)} sites na categoria {category}")
            return sites
            
        except Exception as e:
            logger.error(f"Erro ao buscar sites por categoria: {e}")
            return []
    
    def _clean_domain(self, domain: str) -> str:
        """
        Limpa e valida um domínio
        
        Args:
            domain: Domínio a ser limpo
            
        Returns:
            Domínio limpo ou string vazia se inválido
        """
        try:
            if not domain:
                return ""
            
            # Remover protocolo se presente
            if domain.startswith(('http://', 'https://')):
                domain = domain.split('://', 1)[1]
            
            # Remover www se presente
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Remover barra final
            domain = domain.rstrip('/')
            
            # Validar domínio
            parsed = urlparse(f"https://{domain}")
            if parsed.netloc and '.' in parsed.netloc:
                return parsed.netloc.lower()
            
            return ""
            
        except Exception as e:
            logger.error(f"Erro ao limpar domínio {domain}: {e}")
            return ""
    
    def validate_api_key(self) -> bool:
        """
        Valida se a API key está funcionando
        
        Returns:
            True se a API key é válida, False caso contrário
        """
        try:
            # Testar com um domínio conhecido
            test_domain = "google.com"
            endpoint = f"website/{test_domain}/general-data/overview"
            params = {'country': 'US'}
            
            data = self._make_request(endpoint, params)
            return data is not None
            
        except Exception as e:
            logger.error(f"Erro ao validar API key: {e}")
            return False
    
    def get_api_usage(self) -> Dict:
        """
        Obtém informações sobre o uso da API
        
        Returns:
            Dicionário com informações de uso
        """
        try:
            endpoint = "api-usage"
            data = self._make_request(endpoint)
            
            if data:
                return {
                    'requests_remaining': data.get('requests_remaining', 0),
                    'requests_limit': data.get('requests_limit', 0),
                    'reset_date': data.get('reset_date', ''),
                    'usage_percentage': data.get('usage_percentage', 0.0)
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Erro ao obter uso da API: {e}")
            return {}
