from website.models import Slideshow


def add_slideshow_context(request):
    return {"slideshow": Slideshow.objects.all()}