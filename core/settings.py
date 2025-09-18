# core/settings.py
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------------------------------------------------------
# Básico
# -----------------------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "dev-unsafe")
DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"

# Hosts permitidos
DEFAULT_HOSTS = [
    "127.0.0.1",
    "localhost",
    "radarbr.com",
    "www.radarbr.com",
    "radarbr-site.onrender.com",   # SEM barra
]
ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv("ALLOWED_HOSTS", ",".join(DEFAULT_HOSTS)).split(",")
    if h.strip()
]

# CSRF: sempre com esquema e SEM barra no final
CSRF_TRUSTED_ORIGINS = [f"https://{h}" for h in ALLOWED_HOSTS if "." in h]

SITE_NAME = os.getenv("SITE_NAME", "RadarBR")

# -----------------------------------------------------------------------------
# Apps
# -----------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "siteapp",
]

# -----------------------------------------------------------------------------
# Middleware
# -----------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # serve static em prod
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
                "siteapp.context_processors.site_constants",
            ],
        },
    }
]

WSGI_APPLICATION = "core.wsgi.application"

# -----------------------------------------------------------------------------
# Banco
# -----------------------------------------------------------------------------
import dj_database_url

DATABASES = {
    "default": dj_database_url.parse(
        os.getenv("DATABASE_URL", "sqlite:///db.sqlite3"),
        conn_max_age=600,
        ssl_require=os.getenv("RENDER", "").lower() == "true",
    )
}

# -----------------------------------------------------------------------------
# i18n / tz
# -----------------------------------------------------------------------------
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# -----------------------------------------------------------------------------
# Static / Media (WhiteNoise)
# -----------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]  # se tiver a pasta "static"

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    }
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# -----------------------------------------------------------------------------
# Segurança / Proxy
# -----------------------------------------------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# Força HTTPS no Render (padrão True em prod, False local)
SECURE_SSL_REDIRECT = os.getenv(
    "FORCE_HTTPS",
    "true" if os.getenv("RENDER", "").lower() == "true" else "false",
).lower() == "true"

# -----------------------------------------------------------------------------
# Extras (SEO/Analytics)
# -----------------------------------------------------------------------------
GA4_ID = os.getenv("GA4_ID", "")
SEARCH_CONSOLE_TOKEN = os.getenv("SEARCH_CONSOLE_TOKEN", "")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
