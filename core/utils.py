# core/utils.py
from __future__ import annotations
import os
from urllib.parse import urljoin
from django.conf import settings

_LOCAL_HOSTS = {"127.0.0.1", "localhost", "[::1]"}

def _guess_public_host() -> str:
    """Escolhe um host público válido a partir de ALLOWED_HOSTS."""
    prio = ["www.radarbr.com", "radarbr.com"]
    allowed = [h for h in getattr(settings, "ALLOWED_HOSTS", []) if h]
    # prioridade explícita
    for h in prio:
        if h in allowed:
            return h
    # primeiro host que não seja local e tenha ponto
    for h in allowed:
        base = h.split("://")[-1]
        if base not in _LOCAL_HOSTS and "." in base:
            return h
    # fallback para dev
    return "127.0.0.1:8000"

def site_base_url() -> str:
    """
    Retorna a BASE absoluta do site (com barra no final), priorizando:
      1) settings.SITE_BASE_URL ou env SITE_BASE_URL
      2) scheme por DEBUG (http em dev, https em prod) + host deduzido
    """
    base = getattr(settings, "SITE_BASE_URL", None) or os.getenv("SITE_BASE_URL")
    if base:
        base = base.strip()
        if not base.endswith("/"):
            base += "/"
        return base
    scheme = "http" if getattr(settings, "DEBUG", False) else "https"
    host = _guess_public_host()
    # evita duplicar esquema se o host já vier com http(s)://
    if "://" in host:
        root = host
    else:
        root = f"{scheme}://{host}"
    if not root.endswith("/"):
        root += "/"
    return root

def absolute_url(path: str) -> str:
    """Monta URL absoluta para um path relativo (com ou sem / inicial)."""
    return urljoin(site_base_url(), (path or "").lstrip("/"))

def absolute_sitemap_url() -> str:
    """
    URL absoluta do sitemap. Ajuste SITEMAP_PATH no settings se seu caminho
    não for 'sitemap.xml'.
    """
    sitemap_path = getattr(settings, "SITEMAP_PATH", "sitemap.xml")
    return absolute_url(sitemap_path)
