from django.contrib import sitemaps
from django.urls import reverse
from django.utils.translation import activate


class BecomeAMemberSitemap(sitemaps.Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return [("en", "become-a-member"), ("nl", "become-a-member")]

    def location(self, item):
        activate(item[0])
        return reverse(item[1])
