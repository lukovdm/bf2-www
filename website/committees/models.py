import datetime

from cms.models import PlaceholderField
from django.contrib.auth.models import Permission, User
from django.core.exceptions import ValidationError
from django.db.models import CharField, ManyToManyField, Model, SET_NULL, BooleanField, EmailField, ForeignKey, CASCADE, \
    DateField
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from filer.fields.image import FilerImageField

from utils.translations import ModelTranslateMeta, MultilingualField


class Committee(Model, metaclass=ModelTranslateMeta):
    name = MultilingualField(CharField, max_length=255, verbose_name=_("name"))
    image = FilerImageField(
        verbose_name=_("image"), null=True, blank=True, on_delete=SET_NULL
    )
    description = PlaceholderField("description", verbose_name=_("description"))
    email = EmailField(verbose_name=_("contact email"))

    members = ManyToManyField(User, through="committees.Committee")
    show_members = BooleanField(verbose_name=_("show members"), default=True)

    permissions = ManyToManyField(Permission)

    active = BooleanField(verbose_name=_("Still active"), default=True)

    def __str__(self):
        return f"Committee {self.name}"


class CommitteeMembership(Model):
    user = ForeignKey(User, on_delete=CASCADE, verbose_name=_("User"))
    committee = ForeignKey(Committee, on_delete=CASCADE, verbose_name=_("committee"))

    since = DateField(verbose_name=_("member since"), default=datetime.date.today)
    until = DateField(verbose_name=_("member until"), blank=True, null=True)

    chair = BooleanField(verbose_name=_("chair of committee"), default=False)

    def clean(self):
        if self.until and self.since >= self.until:
            return ValidationError({"until": _("end date can't be before start date")})
        
    def validate_unique(self, **kwargs):
        super().validate_unique(**kwargs)

        if self.chair and self.objects.filter(committee=self.committee, )
