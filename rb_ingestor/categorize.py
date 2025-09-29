# rb_ingestor/categorize.py
"""
Roteia tópico para slug de categoria por regex.
Ordem importa: o primeiro que casar leva.
Fallback: 'geral'
"""
from __future__ import annotations
import re
from typing import List, Tuple

# pares (slug, regex)
_RULES: List[Tuple[str, re.Pattern]] = [
    # Esportes
    ("esportes", re.compile(
        r"\b(brasileir(?:a|ã)o|s[ée]rie\s+[abcd]|libertadores|copa do brasil|futebol|flamengo|gr[êe]mio|palmeiras|corinthians|seleç[aã]o|olimp[ií]adas?)\b",
        re.I)),
    # Economia
    ("economia", re.compile(
        r"\b(d[óo]lar|juros|selic|inflaç[aã]o|pib|bolsa de valores|bovespa|emprego|imposto|irpf|sal[aá]rio m[ií]nimo|aux[ií]lio)\b",
        re.I)),
    # Tecnologia
    ("tecnologia", re.compile(
        r"\b(whatsapp|iphone|android|instagram|facebook|tiktok|google|apple|microsoft|intel|nvidia|chatgpt|ia|intelig[eê]ncia artificial|apps?)\b",
        re.I)),
    # Entretenimento
    ("entretenimento", re.compile(
        r"\b(bbb|novela|s[ée]rie|filme|cinema|celebridade|show|turn[eê]|oscar|festival)\b",
        re.I)),
    # Saúde
    ("saude", re.compile(
        r"\b(dengue|covid|gripe|vacina|sus|sa[úu]de)\b",
        re.I)),
    # Justiça & Segurança
    ("justica-seguranca", re.compile(
        r"\b(pol[ií]cia|pris[aã]o|operaç[aã]o|stf|tse|justi[çc]a|investigaç[aã]o)\b",
        re.I)),
    # Brasil (geral de cidades/estados)
    ("brasil", re.compile(
        r"\b(bras[ií]l|governador|prefeito|c[aã]mara municipal|rodovia|cidades?|estado|munic[ií]pio)\b",
        re.I)),
]

def route_category_for_topic(topic: str) -> str:
    t = (topic or "").strip().lower()
    if not t:
        return "geral"
    for slug, pat in _RULES:
        if pat.search(t):
            return slug
    return "geral"
