from django.contrib.auth.models import User
from django.forms import (
    ModelForm,
    CharField,
    EmailField,
    PasswordInput,
)

from members.models import Member


class BecomeAMemberForm(ModelForm):
    firstname = CharField()
    lastname = CharField()
    email = EmailField()
    password = CharField(widget=PasswordInput())

    class Meta:
        model = Member
        exclude = ["user"]

    def save(self, commit=True):
        member = super().save(commit=False)
        user = User.objects.create_user(
            self.cleaned_data["email"],
            self.cleaned_data["email"],
            self.cleaned_data["password"],
        )
        user.first_name = self.cleaned_data["firstname"]
        user.last_name = self.cleaned_data["lastname"]
        user.is_active = False
        user.save()
        member.user = user
        if commit:
            member.save()
            self.save_m2m()
        return member
