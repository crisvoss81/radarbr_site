from django.http import HttpResponse

def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
        f"Sitemap: {request.build_absolute_uri('/news-sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
