# Configurações do SimilarSiteFinder

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class Config:
    """Configurações base da aplicação"""
    
    # Flask
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Banco de dados
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///sites.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SimilarWeb API
    SIMILARWEB_API_KEY = os.getenv('SIMILARWEB_API_KEY')
    SIMILARWEB_BASE_URL = 'https://api.similarweb.com/v1'
    
    # Configurações de busca
    MAX_RESULTS_PER_SEARCH = int(os.getenv('MAX_RESULTS', '50'))
    DEFAULT_COUNTRY = os.getenv('DEFAULT_COUNTRY', 'BR')
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))
    
    # Configurações de extração de contatos
    CONTACT_EXTRACTION_TIMEOUT = int(os.getenv('CONTACT_TIMEOUT', '10'))
    MAX_CONTACTS_PER_SITE = int(os.getenv('MAX_CONTACTS', '10'))
    
    # User Agent para requisições
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    
    # Configurações de exportação
    EXPORT_FORMATS = ['xlsx', 'csv', 'json']
    MAX_EXPORT_RECORDS = 10000

class DevelopmentConfig(Config):
    """Configurações para desenvolvimento"""
    DEBUG = True

class ProductionConfig(Config):
    """Configurações para produção"""
    DEBUG = False

# Mapeamento de configurações
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
