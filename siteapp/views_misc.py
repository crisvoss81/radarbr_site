# siteapp/views_misc.py
from django.http import HttpResponse

def robots_txt(request):
    host = f"{request.scheme}://{request.get_host()}"
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /buscar/",
        f"Sitemap: {host}/sitemap.xml",
        f"Sitemap: {host}/news-sitemap.xml",
        "",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
