# core/settings.py

from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url
from urllib.parse import urlparse

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

# --- CONFIGURAÇÕES DE SEGURANÇA E AMBIENTE ---
SECRET_KEY = os.getenv("SECRET_KEY", "dev-unsafe")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
UNSPLASH_API_KEY = os.getenv("UNSPLASH_API_KEY")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
GA4_ID = os.getenv("GA4_ID", "")
ADSENSE_CLIENT = os.getenv("ADSENSE_CLIENT", "ca-pub-3913403142217011")
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')

# --- CONFIGURAÇÕES DO SITE ---
SITE_NAME = os.getenv("SITE_NAME", "RadarBR")
SITE_URL = os.getenv("SITE_URL", "http://127.0.0.1:8000")
SITE_BASE_URL = os.getenv("SITE_BASE_URL", "https://www.radarbr.com")
SITEMAP_PATH = os.getenv("SITEMAP_PATH", "sitemap.xml")

# --- APLICAÇÕES INSTALADAS ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.humanize",
    "cloudinary_storage",
    "cloudinary",
    "localflavor",
    "rb_portal",
    "rb_noticias",
    "rb_ingestor",
]

# --- MIDDLEWARE ---
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site_constants",
            "core.context_processors.site_config",
                "core.context_processors.categorias_nav",
            ],
        },
    }
]

WSGI_APPLICATION = "core.wsgi.application"

# --- BANCO DE DADOS ---
# Configuração específica para Render
if os.getenv('RENDER'):
    # Render automaticamente cria DATABASE_URL
    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Desenvolvimento local
    DATABASES = {
        'default': dj_database_url.config(
            default=f'sqlite:///{BASE_DIR / "db.sqlite3"}'
        )
    }

# --- INTERNACIONALIZAÇÃO ---
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# Configurações específicas para o Brasil
USE_L10N = True
USE_THOUSAND_SEPARATOR = True
THOUSAND_SEPARATOR = '.'
DECIMAL_SEPARATOR = ','
NUMBER_GROUPING = 3

# Idiomas suportados
LANGUAGES = [
    ('pt-br', 'Português (Brasil)'),
]

# Formatação de data e hora para o Brasil
DATE_FORMAT = 'd/m/Y'
DATETIME_FORMAT = 'd/m/Y H:i'
SHORT_DATE_FORMAT = 'd/m/Y'
SHORT_DATETIME_FORMAT = 'd/m/Y H:i'

# --- CONFIGURAÇÕES DE SEGURANÇA PARA PRODUÇÃO ---
if os.getenv('RENDER'):
    # Configurações específicas para Render
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# --- ARQUIVOS ESTÁTICOS E DE MÍDIA ---
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = os.getenv('MEDIA_ROOT', BASE_DIR / 'media')

# Configurações do WhiteNoise para produção
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = DEBUG

# Configuração para servir arquivos de mídia em produção (Render)
# Como o Render não tem CDN separado, servimos via Django mesmo
WHITENOISE_SERVE_MEDIA = True

# Configurações adicionais para otimizar o serviço de arquivos
WHITENOISE_MAX_AGE = 31536000  # 1 ano para arquivos estáticos
WHITENOISE_INDEX_FILE = False
WHITENOISE_MANIFEST_STRICT = False

# --- CONFIGURAÇÕES DO CLOUDINARY ---
# Suporta tanto variáveis separadas (CLOUDINARY_CLOUD_NAME, API_KEY, API_SECRET)
# quanto a variável única CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name

_cloudinary_url = os.getenv('CLOUDINARY_URL')
_cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
_api_key = os.getenv('CLOUDINARY_API_KEY')
_api_secret = os.getenv('CLOUDINARY_API_SECRET')

if _cloudinary_url and not (_cloud_name and _api_key and _api_secret):
    try:
        parsed = urlparse(_cloudinary_url)
        # netloc format: api_key:api_secret@cloud_name
        auth, host = parsed.netloc.split('@')
        key, secret = auth.split(':', 1)
        _api_key = _api_key or key
        _api_secret = _api_secret or secret
        _cloud_name = _cloud_name or host
    except Exception:
        # Se parsing falhar, mantém valores existentes (podem estar None)
        pass

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': _cloud_name,
    'API_KEY': _api_key,
    'API_SECRET': _api_secret,
    'SECURE': True,
    'QUALITY': 'auto',
    'FORMAT': 'auto',
    'RESOURCE_TYPE': 'auto',
}

# Configurar Cloudinary como storage padrão para mídia
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"