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
# MOVIDO DE trends_publish.py PARA CÁ, CENTRALIZANDO A LÓGICA
NOISY_PATTERNS = [
    r"^\s*hoje\b",
    r"^\s*amanh(?:ã|a)\b",
    r"^\s*ontem\b",
    r"^\s*que\s+dia",
    r"^\s*que\s+horas",
    r"^\s*(vai\s+chover|chuva|previs[aã]o)\b",
    r"^\s*(tem\s+jogo|jogo\s+do|resultado\s+do\s+jogo)\b",
    r"^\s*not[ií]cias(\s+de\s+hoje)?\s*$",
    # Adicionando filtros mais agressivos para termos comuns que não geram bom conteúdo
    r"tempo\s+agora",
    r"fases\s+da\s+lua",
    r"resultado\s+da\s+lotofacil",
    r"quina",
    r"mega-sena",
]
NOISY_RE = re.compile("|".join(NOISY_PATTERNS), re.I)

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
def fetch_trending_terms(geo: str = "BR", limit: int = 10, debug: bool = False) -> List[str]:
    """
    Busca termos, aplica limpeza/dedup/filtro e retorna a quantidade desejada.
    """
    limit = max(0, int(limit) or 0)
    if not limit:
        return []

    # 1) Tenta buscar uma lista grande de termos brutos de várias fontes
    raw_terms: List[str] = []
    raw_terms += _from_http_realtime(geo)
    raw_terms += _from_http_daily(geo)

    # 2) Fallback para pytrends se as fontes primárias falharem
    if not raw_terms:
        if debug:
            print("[trends.py] INFO: Fontes primárias falharam, tentando pytrends...")
        raw_terms += _from_py_realtime(geo)
        raw_terms += _from_py_today(geo)
        raw_terms += _from_py_trending()
        raw_terms += _from_py_top_charts(geo)

    if debug:
        print(f"[trends.py] DEBUG: Termos brutos coletados ({len(raw_terms)}): {raw_terms}")

    # 3) Limpa, remove duplicatas e filtra o ruído até atingir o limite
    cleaned = _dedupe_keep_order([_clean(t) for t in raw_terms if t])
    
    filtered_terms = []
    for term in cleaned:
        if not _is_noisy(term):
            filtered_terms.append(term)
            if len(filtered_terms) >= limit:
                break # Atingimos o limite desejado
        elif debug:
            print(f"[trends.py] DEBUG: Termo filtrado (ruído): '{term}'")

    return filtered_terms