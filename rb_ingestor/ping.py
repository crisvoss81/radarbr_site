# rb_ingestor/ping.py
import requests

UA = "RadarBRBot/1.0 (+https://radarbr.com)"

def _try_get(url: str, params: dict) -> bool:
    try:
        r = requests.get(
            url,
            params=params,
            headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml"},
            timeout=8,
        )
        return 200 <= r.status_code < 300
    except Exception:
        return False

def ping_search_engines(sitemap_absolute_url: str) -> dict:
    """
    Notifica buscadores sobre atualização do sitemap.
    Retorna flags de sucesso e nunca lança exceções.
    """
    # Google (endpoint clássico; se um dia voltar 404/410, só marca como NOK)
    ok_google = _try_get("https://www.google.com/ping", {"sitemap": sitemap_absolute_url})
    # Bing
    ok_bing   = _try_get("https://www.bing.com/ping",   {"sitemap": sitemap_absolute_url})
    return {"google": ok_google, "bing": ok_bing}
