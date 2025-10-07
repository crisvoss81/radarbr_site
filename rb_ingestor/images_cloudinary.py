"""
Utilitários para upload de imagens remotas (Wikimedia/Openverse/etc.) para o Cloudinary.

Uso principal: upload_remote_to_cloudinary(url) -> secure_url | None
"""
from __future__ import annotations

from typing import Optional

import os
from urllib.parse import urlparse


def _cloudinary_available() -> bool:
    try:
        import cloudinary  # noqa
        if os.getenv("CLOUDINARY_URL"):
            return True
        return bool(
            os.getenv("CLOUDINARY_CLOUD_NAME")
            and os.getenv("CLOUDINARY_API_KEY")
            and os.getenv("CLOUDINARY_API_SECRET")
        )
    except Exception:
        return False


def upload_remote_to_cloudinary(
    remote_url: str,
    *,
    public_id: Optional[str] = None,
    folder: str = "noticias",
    overwrite: bool = True,
    tags: Optional[list[str]] = None,
) -> Optional[str]:
    """
    Faz upload de uma URL remota diretamente para o Cloudinary e retorna a secure_url.
    Retorna None em caso de erro ou se Cloudinary não estiver configurado.
    """
    if not remote_url:
        return None

    if not _cloudinary_available():
        return None

    try:
        import cloudinary
        import cloudinary.uploader as cu

        # Config explicitamente, caso settings não tenha feito o bootstrap
        cloudinary_url = os.getenv("CLOUDINARY_URL")
        if cloudinary_url:
            cloudinary.config(cloudinary_url=cloudinary_url, secure=True)
        else:
            cloudinary.config(
                cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
                api_key=os.getenv("CLOUDINARY_API_KEY"),
                api_secret=os.getenv("CLOUDINARY_API_SECRET"),
                secure=True,
            )

        params = {
            "folder": folder,
            "overwrite": overwrite,
            "resource_type": "image",
            "quality": "auto",
            "fetch_format": "auto",
        }
        if public_id:
            params["public_id"] = public_id
        if tags:
            params["tags"] = tags

        res = cu.upload(remote_url, **params)
        return res.get("secure_url") or res.get("url")
    except Exception:
        return None


