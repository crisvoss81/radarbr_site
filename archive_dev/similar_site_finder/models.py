# Modelos de banco de dados para SimilarSiteFinder

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index

db = SQLAlchemy()

class Site(db.Model):
    """Modelo para armazenar sites encontrados"""
    
    __tablename__ = 'sites'
    
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), nullable=False, unique=True)
    url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(500))
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    country = db.Column(db.String(10), default='BR')
    
    # Métricas do SimilarWeb
    monthly_visits = db.Column(db.BigInteger)
    bounce_rate = db.Column(db.Float)
    pages_per_visit = db.Column(db.Float)
    avg_visit_duration = db.Column(db.Float)
    traffic_rank = db.Column(db.Integer)
    
    # Status e timestamps
    status = db.Column(db.String(20), default='active')  # active, inactive, blocked
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_checked = db.Column(db.DateTime)
    
    # Relacionamentos
    contacts = db.relationship('Contact', backref='site', lazy=True, cascade='all, delete-orphan')
    search_sessions = db.relationship('SearchSession', backref='site', lazy=True)
    
    # Índices para performance
    __table_args__ = (
        Index('idx_domain', 'domain'),
        Index('idx_category', 'category'),
        Index('idx_country', 'country'),
        Index('idx_status', 'status'),
    )
    
    def __repr__(self):
        return f'<Site {self.domain}>'
    
    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            'id': self.id,
            'domain': self.domain,
            'url': self.url,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'country': self.country,
            'monthly_visits': self.monthly_visits,
            'bounce_rate': self.bounce_rate,
            'pages_per_visit': self.pages_per_visit,
            'avg_visit_duration': self.avg_visit_duration,
            'traffic_rank': self.traffic_rank,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_checked': self.last_checked.isoformat() if self.last_checked else None,
            'contacts_count': len(self.contacts)
        }

class Contact(db.Model):
    """Modelo para armazenar contatos extraídos dos sites"""
    
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=False)
    
    # Informações do contato
    contact_type = db.Column(db.String(20), nullable=False)  # whatsapp, email, phone, social
    contact_value = db.Column(db.String(255), nullable=False)
    contact_label = db.Column(db.String(100))  # comercial, suporte, vendas, etc.
    
    # Metadados
    is_verified = db.Column(db.Boolean, default=False)
    is_primary = db.Column(db.Boolean, default=False)  # Contato principal do site
    extraction_method = db.Column(db.String(50))  # Como foi extraído
    confidence_score = db.Column(db.Float, default=0.0)  # Confiança na extração
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Índices
    __table_args__ = (
        Index('idx_site_id', 'site_id'),
        Index('idx_contact_type', 'contact_type'),
        Index('idx_is_primary', 'is_primary'),
        Index('idx_contact_value', 'contact_value'),
    )
    
    def __repr__(self):
        return f'<Contact {self.contact_type}: {self.contact_value}>'
    
    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            'id': self.id,
            'site_id': self.site_id,
            'contact_type': self.contact_type,
            'contact_value': self.contact_value,
            'contact_label': self.contact_label,
            'is_verified': self.is_verified,
            'is_primary': self.is_primary,
            'extraction_method': self.extraction_method,
            'confidence_score': self.confidence_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SearchSession(db.Model):
    """Modelo para rastrear sessões de busca"""
    
    __tablename__ = 'search_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    reference_site = db.Column(db.String(255), nullable=False)
    search_parameters = db.Column(db.JSON)  # Parâmetros da busca
    
    # Resultados
    sites_found = db.Column(db.Integer, default=0)
    new_sites = db.Column(db.Integer, default=0)
    contacts_extracted = db.Column(db.Integer, default=0)
    
    # Status
    status = db.Column(db.String(20), default='running')  # running, completed, failed
    error_message = db.Column(db.Text)
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relacionamentos
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'))
    
    def __repr__(self):
        return f'<SearchSession {self.reference_site}>'
    
    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            'id': self.id,
            'reference_site': self.reference_site,
            'search_parameters': self.search_parameters,
            'sites_found': self.sites_found,
            'new_sites': self.new_sites,
            'contacts_extracted': self.contacts_extracted,
            'status': self.status,
            'error_message': self.error_message,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration': self.get_duration()
        }
    
    def get_duration(self):
        """Retorna a duração da sessão em segundos"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        elif self.started_at:
            return (datetime.utcnow() - self.started_at).total_seconds()
        return 0

class SearchFilter(db.Model):
    """Modelo para filtros de busca salvos"""
    
    __tablename__ = 'search_filters'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Parâmetros do filtro
    country = db.Column(db.String(10))
    category = db.Column(db.String(100))
    min_monthly_visits = db.Column(db.BigInteger)
    max_monthly_visits = db.Column(db.BigInteger)
    max_bounce_rate = db.Column(db.Float)
    min_pages_per_visit = db.Column(db.Float)
    
    # Configurações
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SearchFilter {self.name}>'
    
    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'country': self.country,
            'category': self.category,
            'min_monthly_visits': self.min_monthly_visits,
            'max_monthly_visits': self.max_monthly_visits,
            'max_bounce_rate': self.max_bounce_rate,
            'min_pages_per_visit': self.min_pages_per_visit,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
