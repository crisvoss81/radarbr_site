# core/settings.py — SAFE DEV & PROD

from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

# --- CONFIGURAÇÕES DE SEGURANÇA LENDO DO .ENV ---
SECRET_KEY = os.getenv("SECRET_KEY", "dev-unsafe")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
UNSPLASH_API_KEY = os.getenv("UNSPLASH_API_KEY")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"] # Diz ao Django onde encontrar seus arquivos estáticos durante o desenvolvimento.
STATIC_ROOT = BASE_DIR / "staticfiles"    # Onde `collectstatic` irá copiar os arquivos para produção.
MEDIA_URL = "/media/"
MEDIA_ROOT = os.getenv('MEDIA_ROOT', BASE_DIR / 'media')          # Onde suas imagens de notícias são salvas.

# ALTERADO: Lê o DEBUG do .env. O padrão é False (seguro para produção).
# No seu .env de desenvolvimento, adicione: DEBUG=True
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# ALTERADO: Lê os hosts do .env.
# No seu .env de desenvolvimento, adicione: ALLOWED_HOSTS=127.0.0.1,localhost
# No .env de produção, adicione: ALLOWED_HOSTS=www.radarbr.com,radarbr.com
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1').split(',')


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
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.humanize",
    "rb_portal",
    "rb_noticias",
    "rb_ingestor",
]

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
                "core.context_processors.categorias_nav",
            ],
        },
    }
]

WSGI_APPLICATION = "core.wsgi.application"

# --- BANCO DE DADOS ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# --- INTERNACIONALIZAÇÃO ---
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# --- ARQUIVOS ESTÁTICOS E DE MÍDIA ---
# CORRIGIDO: Bloco duplicado removido.
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# --- OUTRAS CONFIGURAÇÕES ---
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CORRIGIDO: Linha duplicada removida.
# A linha `TEMPLATES[0]["OPTIONS"]["context_processors"] += [...]` foi apagada.