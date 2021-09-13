from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _


from members.models import Member


class Relation(models.Model):
    member_1 = models.ForeignKey(
        Member,
        related_name="relation_1_set",
        on_delete=CASCADE,
        verbose_name=_("member 1"),
    )
    member_2 = models.ForeignKey(
        Member,
        related_name="relation_2_set",
        on_delete=CASCADE,
        verbose_name=_("member 2"),
    )

    class Meta:
        unique_together = (("member_1", "member_2"),)

    def __str__(self):
        return f"{self.member_1} with {self.member_2}"
