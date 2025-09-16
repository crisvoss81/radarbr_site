from django.contrib.syndication.views import Feed
from .models import Post

class LatestPostsFeed(Feed):
    title = "Últimas notícias"
    link = "/"
    description = "Feed das últimas notícias publicadas."

    def items(self):
        return Post.objects.filter(is_published=True)[:30]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt or item.content[:240]

    def item_link(self, item):
        return item.get_absolute_url()
