# Configuração do banco de dados

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    """Inicializa o banco de dados"""
    db.init_app(app)
    migrate.init_app(app, db)
    
    with app.app_context():
        # Criar tabelas se não existirem
        db.create_all()
    
    return db
