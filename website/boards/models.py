from django.core.exceptions import ValidationError
from django.db import models

from members.models import Member


class Board(models.Model):
    start = models.DateField()
    end = models.DateField(blank=True, null=True)

    members = models.ManyToManyField(to=Member, through="BoardMembership")

    picture = models.ImageField()

    def clean(self):
        if self.end:
            if self.start > self.end:
                raise ValidationError(
                    {"start": "Start date should be before end date."}
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
                            "start": "A boards start and end cannot overlap with another board",
                            "end": "A boards start and end cannot overlap with another board",
                        }
                    )
        else:
            for board in Board.objects.all():
                if board is self or board.end is None:
                    continue
                if board.start < self.start < board.end:
                    raise ValidationError(
                        {"start": "A boards start cannot fall in another board"}
                    )

    def __str__(self):
        return f"Board of {self.start.year}"


class BoardMembership(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)

    function = models.CharField(max_length=255)
    email = models.EmailField()

    picture = models.ImageField()