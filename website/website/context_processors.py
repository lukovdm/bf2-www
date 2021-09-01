import random

from website.models import Slideshow


def add_slideshow_context(request):
    slides = Slideshow.objects.all()
    if len(slides) == 0:
        active_index = 0
    else:
        active_index = random.randint(0, len(slides) - 1)
    return {"slideshow": slides, "active_index": active_index}
