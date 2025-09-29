import os, importlib, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE","core.settings")
django.setup()

from django.conf import settings
from django.db import connection

print("DB ENGINE:", settings.DATABASES["default"]["ENGINE"])
print("DB NAME:", settings.DATABASES["default"]["NAME"])

# Lista tabelas
with connection.cursor() as c:
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in c.fetchall()]
print("tables:", tables)

# Conta linhas nas tabelas possíveis
for t in ("rb_noticias_noticia","noticias_noticia"):
    if t in tables:
        with connection.cursor() as c:
            c.execute(f"SELECT COUNT(*) FROM {t}")
            print(f"{t} rows:", c.fetchone()[0])
