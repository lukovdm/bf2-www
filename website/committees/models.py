import datetime

from cms.models import PlaceholderField
from django.contrib.auth.models import Permission, User, Group
from django.core.exceptions import ValidationError
from django.db.models import (
    CharField,
    ManyToManyField,
    Model,
    SET_NULL,
    BooleanField,
    EmailField,
    ForeignKey,
    CASCADE,
    DateField,
    OneToOneField,
    PROTECT,
)
from django.urls import reverse
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

    members = ManyToManyField(User, through="committees.CommitteeMembership")
    show_members = BooleanField(verbose_name=_("show members"), default=True)

    active = BooleanField(verbose_name=_("active committee"), default=True)
    show_in_achievements = BooleanField(
        verbose_name=_("Show committee in personal achievements"), default=True
    )

    perm_group = OneToOneField(
        Group,
        on_delete=PROTECT,
        blank=True,
        null=True,
        verbose_name=_("Permissions"),
    )

    is_staff = BooleanField(verbose_name=_("is staff on the site"), default=False)

    def save(self, **kwargs):
        if self.perm_group is None:
            self.perm_group = Group.objects.create(name=self.name_en)

        super().save(**kwargs)

    def get_absolute_url(self):
        return reverse("committees:detail", kwargs={"pk": self.pk})

    def __str__(self):
        return f"{self.name}"


class CommitteeMembership(Model):
    user = ForeignKey(User, on_delete=CASCADE, verbose_name=_("User"))
    committee = ForeignKey(Committee, on_delete=CASCADE, verbose_name=_("committee"))

    since = DateField(verbose_name=_("member since"), default=datetime.date.today)
    until = DateField(verbose_name=_("member until"), blank=True, null=True)

    chair = BooleanField(verbose_name=_("chair of committee"), default=False)

    def clean(self):
        if self.until and self.since >= self.until:
            return ValidationError(
                {"until": _("until date can't be before since date")}
            )
        if self.until and self.until > timezone.now():
            return ValidationError(
                {"until": _("Until date can't be in the future")}
            )

    def overlaps(self, others):
        for other in others:
            if other == self:
                continue

            if self.until:
                if other.until:
                    if (
                        self.since < other.until <= self.until
                        or other.since <= self.since < other.until
                        or other.since < self.until <= other.until
                    ):
                        return other
                else:
                    if self.since <= other.since < self.until:
                        return other
            else:
                if other.until:
                    if other.since <= self.since < other.until:
                        return other
                else:
                    return other
        return None

    def validate_unique(self, **kwargs):
        super().validate_unique(**kwargs)

        # Check if there is an overlapping chair
        if self.chair:
            if chair := self.overlaps(
                CommitteeMembership.objects.filter(committee=self.committee, chair=True)
            ):
                raise ValidationError(
                    {
                        "since": _(
                            "A committees cannot have two chairs during the same period, namely: "
                        )
                        + chair.user.get_full_name(),
                        "until": _(
                            "A committees cannot have two chairs during the same period, namely: "
                        )
                        + chair.user.get_full_name(),
                    }
                )

        # Check if there are no overlapping memberships of the same person in the same committee
        if self.overlaps(
            CommitteeMembership.objects.filter(committee=self.committee, user=self.user)
        ):
            raise ValidationError(
                {
                    "since": _(
                        "A user cannot have overlapping memberships in the same committee"
                    ),
                    "until": _(
                        "A user cannot have overlapping memberships in the same committee"
                    ),
                }
            )

    def save(self, **kwargs):
        super().save(**kwargs)
        self.user.is_staff = (
            self.user.committeemembership_set.exclude(until__lte=timezone.now())
            .exclude(committee__is_staff=False)
            .exists()
        )

        self.committee.perm_group.user_set.set(
            User.objects.filter(committee=self.committee).exclude(
                committeemembership__until__lte=timezone.now()
            )
        )

        self.user.save()
        self.committee.save()

    def __str__(self):
        return f"{self.user}{' past' if self.until else ''} member of {self.committee}"
