# rb_ingestor/images_free.py
"""
Busca imagem livre para um tópico usando Wikimedia e Openverse.
- Faz download com User-Agent próprio
- Processa para 1200x630 (cover), JPEG de qualidade 85
- Retorna dict: filename, content (ContentFile), credito, licenca, fonte_url
"""
from __future__ import annotations
import io
import re
import hashlib
import requests
from typing import Optional, Dict
from PIL import Image, ImageOps
from django.core.files.base import ContentFile
from slugify import slugify

UA = "RadarBRBot/1.0 (+https://radarbr.com)"
HTTP_TIMEOUT = 12

def _hash(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8", "ignore")).hexdigest()[:8]

def _download_bytes(url: str) -> Optional[bytes]:
    try:
        r = requests.get(url, headers={"User-Agent": UA, "Referer": "https://radarbr.com"}, timeout=HTTP_TIMEOUT)
        r.raise_for_status()
        ct = (r.headers.get("Content-Type") or "").lower()
        if "image" not in ct:
            return None
        return r.content
    except Exception:
        return None

def _process_to_1200x630(data: bytes) -> Optional[bytes]:
    try:
        im = Image.open(io.BytesIO(data))
        im = ImageOps.exif_transpose(im)
        # força RGB (remove alpha)
        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")
        elif im.mode == "L":
            im = im.convert("RGB")

        target_w, target_h = 1200, 630
        src_w, src_h = im.size
        src_ratio = src_w / src_h
        tgt_ratio = target_w / target_h

        # cover: corta centro
        if src_ratio > tgt_ratio:
            # imagem "mais larga": ajusta altura e corta largura
            new_h = target_h
            new_w = int(new_h * src_ratio)
        else:
            new_w = target_w
            new_h = int(new_w / src_ratio)

        im_resized = im.resize((new_w, new_h), Image.LANCZOS)
        left = (new_w - target_w) // 2
        top = (new_h - target_h) // 2
        im_cropped = im_resized.crop((left, top, left + target_w, top + target_h))

        out = io.BytesIO()
        im_cropped.save(out, format="JPEG", quality=85, optimize=True)
        return out.getvalue()
    except Exception:
        return None

def _candidate_filename(topic: str, source_tag: str = "img") -> str:
    base = slugify(topic) or "imagem"
    return f"{source_tag}_{base}_{_hash(topic)}_1200x630.jpg"

# ----------------------- Wikimedia -----------------------

def _wikimedia_search(term: str) -> Optional[Dict]:
    """
    Busca arquivos (namespace 6) compatíveis na Wikimedia.
    Retorna dict com url, credito, licenca, fonte_url.
    """
    API = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": term,
        "gsrlimit": 6,
        "gsrnamespace": 6,  # apenas 'File:'
        "prop": "imageinfo|info",
        "inprop": "url",
        "iiprop": "url|extmetadata",
        "iiurlwidth": 1600,
        "origin": "*",
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
        if not infos:
            continue
        info = infos[0]
        # pega URL grande (url) ou thumb (thumburl)
        img_url = info.get("url") or info.get("thumburl")
        if not img_url:
            continue
        ext = (info.get("extmetadata") or {})
        artist = (ext.get("Artist") or {}).get("value") or ""
        credit = (ext.get("Credit") or {}).get("value") or ""
        license_short = (ext.get("LicenseShortName") or {}).get("value") or ""
        usage = (ext.get("UsageTerms") or {}).get("value") or ""
        page_url = page.get("fullurl") or info.get("descriptionshorturl") or img_url

        # Limpa tags simples de crédito
        def _strip_html(x: str) -> str:
            return re.sub(r"<[^>]+>", "", x or "").strip()

        credito = _strip_html(artist or credit) or "Wikimedia Commons"
        licenca = license_short or usage or "CC"
        return {"url": img_url, "credito": credito, "licenca": licenca, "fonte_url": page_url}

    return None

# ----------------------- Openverse -----------------------

def _openverse_search(term: str) -> Optional[Dict]:
    """
    Busca no Openverse (WordPress) sem API key.
    Filtra licenças reutilizáveis.
    """
    API = "https://api.openverse.org/v1/images"
    params = {
        "q": term,
        "license_type": "cc_publicdomain,cc_by,cc_by_sa",
        "page_size": 8,
        "format": "json",
        "fields": "title,creator,url,license,license_version,foreign_landing_url",
    }
    try:
        r = requests.get(API, params=params, headers={"User-Agent": UA}, timeout=HTTP_TIMEOUT)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return None

    results = data.get("results") or []
    for item in results:
        url = item.get("url")
        if not url:
            continue
        creator = item.get("creator") or "Openverse"
        lic = item.get("license") or ""
        ver = item.get("license_version") or ""
        licenca = f"{lic.upper()} {ver}".strip()
        fonte = item.get("foreign_landing_url") or url
        return {"url": url, "credito": creator, "licenca": licenca, "fonte_url": fonte}

    return None

# ----------------------- Orquestração pública -----------------------

def pick_image(topic: str) -> Dict:
    """
    Tenta Wikimedia; se falhar, tenta Openverse.
    Se baixar e processar, devolve dict completo para salvar no modelo.
    Se nada der certo, retorna placeholders com content=None.
    """
    topic = (topic or "").strip()
    if not topic:
        return {"filename": "", "content": None, "credito": "", "licenca": "", "fonte_url": ""}

    info = _wikimedia_search(topic) or _openverse_search(topic)
    if not info or not info.get("url"):
        return {"filename": "", "content": None, "credito": "", "licenca": "", "fonte_url": ""}

    raw = _download_bytes(info["url"])
    if not raw:
        return {"filename": "", "content": None, "credito": "", "licenca": "", "fonte_url": info.get("fonte_url", "")}

    processed = _process_to_1200x630(raw)
    if not processed:
        return {"filename": "", "content": None, "credito": "", "licenca": "", "fonte_url": info.get("fonte_url", "")}

    filename = _candidate_filename(topic, "img")
    return {
        "filename": filename,
        "content": ContentFile(processed, name=filename),
        "credito": info.get("credito", ""),
        "licenca": info.get("licenca", ""),
        "fonte_url": info.get("fonte_url", ""),
    }
