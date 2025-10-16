#!/usr/bin/env python3
"""
Script de inicialização do SimilarSiteFinder
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 ou superior é necessário")
        print(f"Versão atual: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} detectado")
    return True

def install_dependencies():
    """Instala as dependências do projeto"""
    print("📦 Instalando dependências...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependências instaladas com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False

def setup_environment():
    """Configura o arquivo de ambiente"""
    env_file = Path(".env")
    env_example = Path("env_example.txt")
    
    if not env_file.exists() and env_example.exists():
        print("⚙️ Configurando arquivo de ambiente...")
        shutil.copy(env_example, env_file)
        print("✅ Arquivo .env criado")
        print("⚠️ IMPORTANTE: Edite o arquivo .env com suas configurações:")
        print("   - SIMILARWEB_API_KEY: Sua chave da API SimilarWeb")
        print("   - FLASK_SECRET_KEY: Uma chave secreta para o Flask")
        return True
    elif env_file.exists():
        print("✅ Arquivo .env já existe")
        return True
    else:
        print("❌ Arquivo env_example.txt não encontrado")
        return False

def create_directories():
    """Cria diretórios necessários"""
    directories = ["static", "static/css", "static/js", "static/images", "templates"]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Diretórios criados")

def initialize_database():
    """Inicializa o banco de dados"""
    print("🗄️ Inicializando banco de dados...")
    try:
        from app import create_app
        from models import db
        
        app = create_app()
        with app.app_context():
            db.create_all()
        
        print("✅ Banco de dados inicializado")
        return True
    except Exception as e:
        print(f"❌ Erro ao inicializar banco de dados: {e}")
        return False

def test_similarweb_api():
    """Testa a conexão com a API SimilarWeb"""
    print("🔍 Testando conexão com SimilarWeb API...")
    try:
        from similarweb_api import SimilarWebAPI
        from config import Config
        
        api_key = os.getenv('SIMILARWEB_API_KEY')
        if not api_key or api_key == 'sua_chave_api_similarweb_aqui':
            print("⚠️ SIMILARWEB_API_KEY não configurada no arquivo .env")
            print("   Configure sua chave da API SimilarWeb para usar o sistema")
            return False
        
        api = SimilarWebAPI(api_key)
        if api.validate_api_key():
            print("✅ Conexão com SimilarWeb API funcionando")
            return True
        else:
            print("❌ Falha na validação da API SimilarWeb")
            print("   Verifique se a chave da API está correta")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar API SimilarWeb: {e}")
        return False

def main():
    """Função principal de inicialização"""
    print("🚀 Inicializando SimilarSiteFinder...")
    print("=" * 50)
    
    # Verificar versão do Python
    if not check_python_version():
        return False
    
    # Criar diretórios
    create_directories()
    
    # Instalar dependências
    if not install_dependencies():
        return False
    
    # Configurar ambiente
    if not setup_environment():
        return False
    
    # Inicializar banco de dados
    if not initialize_database():
        return False
    
    # Testar API SimilarWeb
    test_similarweb_api()
    
    print("=" * 50)
    print("🎉 SimilarSiteFinder inicializado com sucesso!")
    print("\n📋 Próximos passos:")
    print("1. Edite o arquivo .env com suas configurações")
    print("2. Execute: python app.py")
    print("3. Acesse: http://localhost:5000")
    print("\n📚 Documentação completa no README.md")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
