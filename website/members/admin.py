from cms.utils.mail import send_mail
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django_mail_template.models import Configuration
from import_export import resources
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportMixin

from .models import Member, OtherClub
from .tokens import AccountActivationTokenGenerator


class UserResource(resources.ModelResource):
    class Meta:
        model = User
        import_id_fields = ("email",)
        fields = (
            "first_name",
            "last_name",
            "email",
            "member__birthday",
            "member__phone_number",
            "member__street_address",
            "member__postcode",
            "member__city",
            "member__student_type",
            "member__sports_card_number",
            "member__graduation_date",
            "member__other_club",
        )

    def init_instance(self, row=None):
        user = User.objects.create_user(
            username=row["email"],
        )
        user.set_unusable_password()
        user.save()
        Member.objects.create(
            user=user,
            birthday=parse_date(row["member__birthday"]),
            phone_number=row["member__phone_number"],
            street_address=row["member__street_address"],
            postcode=row["member__postcode"],
            city=row["member__city"],
            student_type=row["member__student_type"],
            sports_card_number=row["member__sports_card_number"],
            graduation_date=parse_date(row["member__graduation_date"]),
        )
        return user


class MemberInline(admin.StackedInline):
    classes = ["collapse"]
    model = Member
    can_delete = False


class UserAdmin(ImportExportMixin, BaseUserAdmin):
    inlines = (MemberInline,)
    resource_class = UserResource
    actions = ["send_password_email"]

    fieldsets = (
        (
            _("Personal"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "username",
                    "password",
                    "is_active",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                    "date_joined",
                    "last_login",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def send_password_email(self, request, queryset):
        current_site = get_current_site(request)
        domain = current_site.domain
        use_https = "https" if request.is_secure() else "http"
        base = f"{use_https}://{domain}"

        token_generator = AccountActivationTokenGenerator()

        mail_template = Configuration.get_mail_template("activate_account")

        for user in queryset:
            link = base + reverse(
                "activate-account",
                kwargs={
                    "uidb64": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": token_generator.make_token(user),
                }
            )

            mail_template.to = user.email
            mail_template.send({
                "name": user.get_full_name(),
                "link": link
            })

            user.is_active = True
            user.set_unusable_password()
            user.save()


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(OtherClub)
class OtherClubAdmin(admin.ModelAdmin):
    pass
