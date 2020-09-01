from cms.models import PlaceholderField
from django.contrib.auth.models import User
from django.db.models import (
    Model,
    CharField,
    DateTimeField,
    IntegerField,
    OneToOneField,
    CASCADE,
    BooleanField,
    ForeignKey,
)
from django.utils.timezone import now


class Event(Model):
    """An event with no registrations in itself"""

    name = CharField(max_length=255)
    date = DateTimeField()
    location = CharField(max_length=255)
    description = PlaceholderField("description")

    limit = IntegerField(null=True, name="participant limit")
    cost = IntegerField(null=True)
    registration_start = DateTimeField(default=now, null=True)
    registration_end = DateTimeField(null=True)


class Registration(Model):
    """Registration of a user to a registrable event"""

    event = ForeignKey(Event, CASCADE)
    user = ForeignKey(User, CASCADE)

    date = DateTimeField(default=now)
    has_payed = BooleanField(null=True)
