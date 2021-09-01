from website.models import Slideshow
from django.contrib import admin


@admin.register(Slideshow)
class SlideshowAdmin(admin.ModelAdmin):
    pass
