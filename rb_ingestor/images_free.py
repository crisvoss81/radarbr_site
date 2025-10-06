# rb_ingestor/images_free.py
"""
Busca uma URL de imagem livre para um tópico usando Wikimedia e Openverse.
Não faz download nem processamento, apenas retorna um dicionário com a URL
e metadados (crédito, licença, etc.).
"""
from __future__ import annotations
import re
import requests
from typing import Optional, Dict

UA = "RadarBRBot/1.0 (+https://radarbr.com)"
HTTP_TIMEOUT = 12

# ----------------------- Wikimedia -----------------------

def _wikimedia_search(term: str) -> Optional[Dict]:
    """
    Busca arquivos na Wikimedia e retorna a URL da imagem e metadados.
    """
    API = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": term, "gsrlimit": 6, "gsrnamespace": 6,
        "prop": "imageinfo|info", "inprop": "url", "iiprop": "url|extmetadata",
        "iiurlwidth": 1600, "origin": "*",
    }
    try:
        r = requests.get(API, params=params, headers={"User-Agent": UA}, timeout=HTTP_TIMEOUT)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return None

    pages = (data.get("query") or {}).get("pages") or {}
    for _, page in pages.items():
        infos = page.get("imageinfo") or []
        if not infos: continue
        info = infos[0]
        img_url = info.get("url") or info.get("thumburl")
        if not img_url: continue

        ext = info.get("extmetadata") or {}
        artist = (ext.get("Artist") or {}).get("value") or ""
        credit = (ext.get("Credit") or {}).get("value") or ""
        license_short = (ext.get("LicenseShortName") or {}).get("value") or ""
        page_url = page.get("fullurl") or info.get("descriptionshorturl") or img_url

        def _strip_html(x: str) -> str:
            return re.sub(r"<[^>]+>", "", x or "").strip()

        credito = _strip_html(artist or credit) or "Wikimedia Commons"
        return {"url": img_url, "credito": credito, "licenca": license_short, "fonte_url": page_url}

    return None

# ----------------------- Openverse -----------------------

def _openverse_search(term: str) -> Optional[Dict]:
    """
    Busca no Openverse e retorna a URL da imagem e metadados.
    """
    API = "https://api.openverse.org/v1/images"
    params = {
        "q": term, "license_type": "cc_publicdomain,cc_by,cc_by_sa",
        "page_size": 8, "format": "json",
        "fields": "creator,url,license,license_version,foreign_landing_url",
    }
    try:
        r = requests.get(API, params=params, headers={"User-Agent": UA}, timeout=HTTP_TIMEOUT)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return None

    for item in (data.get("results") or []):
        url = item.get("url")
        if not url: continue
        
        creator = item.get("creator") or "Openverse"
        lic = item.get("license") or ""
        ver = item.get("license_version") or ""
        licenca = f"{lic.upper()} {ver}".strip()
        fonte = item.get("foreign_landing_url") or url
        return {"url": url, "credito": creator, "licenca": licenca, "fonte_url": fonte}

    return None

# ----------------------- Orquestração pública -----------------------

def pick_image(topic: str) -> Optional[Dict]:
    """
    Tenta Wikimedia; se falhar, tenta Openverse.
    Retorna um dicionário com a URL e metadados da imagem encontrada, ou None.
    """
    topic = (topic or "").strip()
    if not topic:
        return None

    # Tenta encontrar uma imagem, primeiro na Wikimedia, depois no Openverse
    image_info = _wikimedia_search(topic) or _openverse_search(topic)

    return image_info