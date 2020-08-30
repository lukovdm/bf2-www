from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm

from members.models import Member


class BecomeAMemberForm(ModelForm):
    firstname = forms.CharField()
    lastname = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = Member
        exclude = ["user"]

    def save(self, commit=True):
        member = super().save(commit=False)
        user = User.objects.create_user(
            self.cleaned_data["firstname"][0] + self.cleaned_data["lastname"],
            self.cleaned_data["email"],
            self.cleaned_data["password"],
        )
        user.firstname = self.cleaned_data["firstname"]
        user.lastname = self.cleaned_data["lastname"]
        user.save()
        member.user = user
        if commit:
            member.save()
            self.save_m2m()
        return member
