from django.db import models
from filer.fields.image import FilerImageField
from django.utils.translation import gettext_lazy as _


class Slideshow(models.Model):
    slideshow_image = FilerImageField(verbose_name=_("image"), on_delete=models.CASCADE)
    image_description = models.TextField(verbose_name=_("description"))

    def __str__(self):
        return "Slide: " + self.image_description
