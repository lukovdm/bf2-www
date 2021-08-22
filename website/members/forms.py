from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import (
    get_password_validators,
    password_validators_help_text_html,
    validate_password,
)
from django.core.exceptions import ValidationError
from django.forms import (
    ModelForm,
    CharField,
    EmailField,
    PasswordInput,
    BooleanField,
)
from django_mail_template.models import Configuration
from django.core.mail import mail_admins
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from members.models import Member


class BecomeAMemberForm(ModelForm):
    firstname = CharField(label=_("First name"))
    lastname = CharField(label=_("Last name"))
    email = EmailField(label=_("E-mail"))
    password = CharField(
        widget=PasswordInput(),
        help_text=password_validators_help_text_html(),
    )
    data_registration = BooleanField(required=True)

    class Meta:
        model = Member
        help_texts = {
            "google_email": _(
                "This will be used to gain access to the google drive and might be the same as your regular e-mail"
            ),
        }
        exclude = ["user"]

    def clean_password(self):
        validate_password(self.data["password"], self.instance)
        return self.data["password"]

    def save(self, commit=True, *args, **kwargs):
        member = super().save(commit=False)
        user = User.objects.create_user(
            self.cleaned_data["email"],
            self.cleaned_data["email"],
        )
        user.set_password(self.cleaned_data["password"])
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
                        "phone_number": member.phone_number,
                        "email": user.email,
                        "google_email": member.google_email,
                        "birthday": member.birthday,
                        "sports_card_number": member.sports_card_number,
                        "link_to_member": link,
                        "gender": member.gender,
                        "pronouns": member.pronouns,
                        "other_club": member.other_club,
                    }
                )
            else:
                mail_admins(
                    """No template or configuration for sign up""",
                    """Someone signed up using the sign up form on the website. But either the configuration is missing or there is no 
                    template connected to this configuration. Please solve this problem now!""",
                )
                if not Configuration.objects.filter(process="new_member").exists():
                    Configuration.objects.create(
                        process="new_member",
                        description="""This configuration is used to send a mail to the secretary when a new member signed up.
                        You can use the following variables: \n
                        {name}: the name of the new member \n
                        {phone_number}: the phone number of the member \n
                        {email}: the email of the member \n
                        {google_email}: the google email of the member \n
                        {birthday}: the birthday of the member \n
                        {sports_card_number}: the sports card number of the member \n 
                        {link_to_member}: the link the this specific member \n
                        {pronouns}: the pronouns of the member \n
                        {other_club}: shows if member is also part of another frisbee club
                        """,
                    )
        return member
