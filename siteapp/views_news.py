# siteapp/views_news.py
from django.http import HttpResponse

def news_sitemap(request):
    # versão mínima só pra destravar as migrações
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" ' \
          'xmlns:news="http://www.google.com/schemas/sitemap-news/0.9"></urlset>'
    return HttpResponse(xml, content_type="application/xml")
