from django.conf import settings

def site_constants(request):
    return {
        "SITE_NAME": getattr(settings, "SITE_NAME", "RadarBR"),
        "GA4_ID": getattr(settings, "GA4_ID", ""),
        "SEARCH_CONSOLE_TOKEN": getattr(settings, "SEARCH_CONSOLE_TOKEN", ""),
    }
