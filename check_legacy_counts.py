import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE","core.settings")
django.setup()
from django.db import connection

def table_exists(name: str) -> bool:
    # sem parâmetros para evitar bug do debug SQL do Django no SQLite
    with connection.cursor() as c:
        c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{name}'")
        return c.fetchone() is not None

for t in ("siteapp_post","noticias_noticia"):
    if table_exists(t):
        with connection.cursor() as c:
            c.execute(f"SELECT COUNT(*) FROM {t}")
            print(t, "rows:", c.fetchone()[0])
    else:
        print(t, "não existe")
