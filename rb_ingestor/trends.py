# rb_ingestor/trends.py
"""
Coleta tópicos em alta no Google (BR) com múltiplos fallbacks e filtros.
Ordem:
  1) HTTP realtime: /trends/api/realtimetrends
  2) HTTP daily:    /trends/api/dailytrends
  3) pytrends: realtime/today/trending_searches/top_charts
Retorna lista de termos (strings) já limpos, deduplicados e filtrados.
"""
from __future__ import annotations
import re
import json
import datetime as dt
from typing import Iterable, List, Optional

# --- HTTP fallback (Google Trends endpoints) ---
import requests

UA = "RadarBRBot/1.0 (+https://radarbr.com)"
HTTP_TIMEOUT = 10

# pytrends (opcional)
try:
    from pytrends.request import TrendReq
except Exception:
    TrendReq = None

# ----------------- filtros de ruído -----------------
NOISY_PATTERNS = [
    r"^\s*hoje\b",
    r"^\s*amanh(?:ã|a)\b",
    r"^\s*ontem\b",
    r"^\s*que\s+dia",
    r"^\s*que\s+horas",
    r"^\s*(vai\s+chover|chuva|previs[aã]o)\b",
    r"^\s*(tem\s+jogo|jogo\s+do|resultado\s+do\s+jogo)\b",
    r"^\s*not[ií]cias(\s+de\s+hoje)?\s*$",
]
NOISY_RE = re.compile("|".join(NOSY if (NOSY := NOISY_PATTERNS) else []), re.I)

def _is_noisy(term: str) -> bool:
    t = (term or "").strip()
    if len(t) <= 3:
        return True
    return bool(NOISY_RE.search(t))

# ----------------- helpers -----------------
def _clean(term: str) -> str:
    t = (term or "").strip()
    t = re.sub(r"\s+", " ", t)
    return t

def _dedupe_keep_order(items: Iterable[str]) -> List[str]:
    seen, out = set(), []
    for x in items:
        k = (x or "").strip().lower()
        if not k or k in seen:
            continue
        seen.add(k)
        out.append((x or "").strip())
    return out

def _http_get_json(url: str, params: dict) -> Optional[dict]:
    """
    Baixa JSON dos endpoints /trends/api/* que retornam com prefixo )]}',
    removendo o prefixo antes de json.loads.
    """
    try:
        r = requests.get(url, params=params, headers={"User-Agent": UA}, timeout=HTTP_TIMEOUT)
        r.raise_for_status()
        text = r.text.lstrip(")]}',\n ")
        return json.loads(text)
    except Exception:
        return None

# ----------------- fontes HTTP (oficiais do site) -----------------
def _from_http_realtime(geo: str) -> List[str]:
    """
    https://trends.google.com/trends/api/realtimetrends?hl=pt-BR&tz=-180&cat=all&fi=0&fs=0&geo=BR&ri=300&rs=20
    """
    url = "https://trends.google.com/trends/api/realtimetrends"
    params = {"hl": "pt-BR", "tz": -180, "cat": "all", "fi": 0, "fs": 0, "geo": geo.upper(), "ri": 300, "rs": 20}
    data = _http_get_json(url, params) or {}
    out: List[str] = []
    try:
        stories = (((data.get("storySummaries") or {}).get("trendingStories")) or [])
        for s in stories:
            # tente título principal; se não, primeira entidade
            title = (s.get("title") or "").strip()
            if not title:
                ents = s.get("entityNames") or []
                if ents:
                    title = str(ents[0]).strip()
            if title:
                out.append(title)
    except Exception:
        pass
    return out

def _from_http_daily(geo: str) -> List[str]:
    """
    https://trends.google.com/trends/api/dailytrends?hl=pt-BR&tz=-180&geo=BR&ns=15
    """
    url = "https://trends.google.com/trends/api/dailytrends"
    params = {"hl": "pt-BR", "tz": -180, "geo": geo.upper(), "ns": 15}
    data = _http_get_json(url, params) or {}
    out: List[str] = []
    try:
        days = (data.get("default") or {}).get("trendingSearchesDays") or []
        if days:
            for item in (days[0].get("trendingSearches") or []):
                title = (((item.get("title") or {}).get("query")) or "").strip()
                if title:
                    out.append(title)
    except Exception:
        pass
    return out

# ----------------- fontes pytrends -----------------
def _from_py_realtime(geo: str) -> List[str]:
    if TrendReq is None:
        return []
    try:
        tr = TrendReq(hl="pt-BR", tz=-180)
        df = tr.realtime_trending_searches(pn=geo.upper())
        if df is not None and "title" in df.columns:
            return [str(x) for x in df["title"].tolist()]
    except Exception:
        return []
    return []

def _from_py_today(geo: str) -> List[str]:
    if TrendReq is None:
        return []
    try:
        tr = TrendReq(hl="pt-BR", tz=-180)
        df = tr.today_searches(pn=geo.upper())
        if df is None:
            return []
        if hasattr(df, "tolist"):
            return [str(x) for x in df.tolist()]
        if "title" in df.columns:
            return [str(x) for x in df["title"].tolist()]
    except Exception:
        return []
    return []

def _from_py_trending() -> List[str]:
    if TrendReq is None:
        return []
    try:
        tr = TrendReq(hl="pt-BR", tz=-180)
        df = tr.trending_searches(pn="brazil")
        if df is not None and df.columns.size:
            col = df.columns[0]
            return [str(x) for x in df[col].tolist()]
    except Exception:
        return []
    return []

def _from_py_top_charts(geo: str) -> List[str]:
    if TrendReq is None:
        return []
    try:
        tr = TrendReq(hl="pt-BR", tz=-180)
        year = dt.date.today().year
        df = tr.top_charts(year, hl="pt-BR", tz=-180, geo=geo.upper())
        if df is None:
            return []
        col = "title" if "title" in df.columns else ("topic_title" if "topic_title" in df.columns else None)
        if col:
            return [str(x) for x in df[col].tolist()]
    except Exception:
        return []
    return []

# ----------------- função pública -----------------
def fetch_trending_terms(geo: str = "BR", limit: int = 10) -> List[str]:
    """
    Busca termos e aplica limpeza/dedup/filtro.
    Retorna no máximo `limit` itens.
    """
    limit = max(0, int(limit) or 0)

    # 1) HTTP realtime/daily
    terms: List[str] = []
    terms += _from_http_realtime(geo)
    terms += _from_http_daily(geo)

    # 2) pytrends (se disponível)
    if not terms:
        terms += _from_py_realtime(geo)
        terms += _from_py_today(geo)
        terms += _from_py_trending()
        terms += _from_py_top_charts(geo)

    # limpeza
    cleaned = [_clean(t) for t in terms if t]
    cleaned = _dedupe_keep_order(cleaned)

    # filtro de ruído
    filtered = [t for t in cleaned if not _is_noisy(t)]

    return filtered[:limit]
