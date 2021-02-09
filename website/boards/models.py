from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from members.models import Member
from utils.translations import ModelTranslateMeta, MultilingualField


class Board(models.Model):
    start = models.DateField(verbose_name=_("start"))
    end = models.DateField(blank=True, null=True, verbose_name=_("end"))

    picture = models.ImageField(blank=True, null=True, verbose_name=_("picture"))

    def clean(self):
        if self.end:
            if self.start > self.end:
                raise ValidationError(
                    {"start": _("Start date should be before end date.")}
                )

            for board in Board.objects.all():
                if board is self:
                    continue
                if (
                    board.end
                    and (
                        self.start < board.end <= self.end
                        or board.start <= self.start < board.end
                        or board.start < self.end <= board.end
                    )
                    or self.start <= board.start < self.end
                ):
                    raise ValidationError(
                        {
                            "start": _(
                                "A boards start and end cannot overlap with another board"
                            ),
                            "end": _(
                                "A boards start and end cannot overlap with another board"
                            ),
                        }
                    )
        else:
            for board in Board.objects.all():
                if board is self or board.end is None:
                    continue
                if board.start < self.start < board.end:
                    raise ValidationError(
                        {"start": _("A boards start cannot fall in another board")}
                    )

    def __str__(self):
        return _("Board of") + " " + str(self.start.year)


class BoardMembership(models.Model, metaclass=ModelTranslateMeta):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, verbose_name=_("board"))

    member = models.ForeignKey(
        Member,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("member"),
    )
    name = models.CharField(
        max_length=255, blank=True, null=True, verbose_name=_("name")
    )

    function = MultilingualField(
        models.CharField, max_length=255, verbose_name=_("function")
    )
    email = models.EmailField(verbose_name=_("email"))
    picture = models.ImageField(blank=True, null=True, verbose_name=_("picture"))

    def clean(self):
        if self.member is not None and self.name is not None:
            raise ValidationError(
                {
                    "member": _("Either member or name have to be filled, not both"),
                    "name": _("Either member or name have to be filled, not both"),
                }
            )

        if self.member is None and self.name is None:
            raise ValidationError(
                {
                    "member": _("Either member or name is required"),
                    "name": _("Either member or name is required"),
                }
            )
