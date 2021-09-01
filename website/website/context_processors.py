import random

from website.models import Slideshow


def add_slideshow_context(request):
    slides = Slideshow.objects.all()
    return {"slideshow": slides, "active_index": random.randint(0, len(slides) - 1)}
