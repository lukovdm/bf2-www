from django.contrib.auth.models import User
from django.forms import (
    ModelForm,
    CharField,
    EmailField,
    PasswordInput,
)
from django_mail_template.models import Configuration
from django.core.exceptions import ValidationError
from django.core.mail import mail_admins
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


from members.models import Member


class BecomeAMemberForm(ModelForm):
    firstname = CharField()
    lastname = CharField()
    email = EmailField()
    password = CharField(widget=PasswordInput())

    class Meta:
        model = Member
        exclude = ["user"]

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

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

            template = Configuration.get_mail_template("new_member")
            if template:
                link = reverse("admin:auth_user_change", args=(user.id,))
                template.send(
                    {
                        "name": user.get_full_name(),
                        "phone_number": member.phone_number(),
                        "email": user.email(),
                        "birthday": member.birthday(),
                        "sports_card_number": member.sports_card_number(),
                        "link_to_member": link,
                    }
                )
            else:
                mail_admins(
                    """No template or configuration for sign up""",
                    """Either the configuration or template for sign up is missing or 
                not connected. Please solve this problem now!""",
                )
                if not Configuration.objects.filter(process="new_member").exists():
                    Configuration.objects.create(
                        process="new_member",
                        description="""This configuration is used to send a mail to the secretary when a new member signed up.
                        You can use the following variables:
                        {name}: the name of the new member
                        """,
                    )
        return member
