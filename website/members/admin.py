from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django_mail_template.models import Configuration
from import_export import resources
from import_export.admin import ImportExportMixin
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied, ValidationError

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
            "member__preferred_language",
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
    change_form_template = "members/admin/change_form.html"
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

    def send_accept_email(self, request, obj):
        templates = {}
        success = True
        for lang, display in settings.LANGUAGES:
            t = Configuration.get_mail_template("accept_account_" + lang)
            if t:
                templates[lang] = t
            elif Configuration.objects.filter(
                process="accept_account_" + lang
            ).exists():
                messages.error(
                    request,
                    (
                        _(
                            "No email template has been attached to the %s configuration, you have to create one first"
                        )
                        % lang
                    ),
                )
                success = False
            else:
                Configuration.objects.create(
                    process="accept_account_" + lang,
                    description="""This configuration is used to send accept account email for new users.
                    You can use the following variables:
                    {name}: the name of the user
                    """,
                )
                messages.error(
                    request,
                    (
                        _(
                            "No configuration exists for %s and has been created. You do have to add a template yourself"
                        )
                        % lang
                    ),
                )
                success = False
        if not success:
            return False
        lang = obj.member.preferred_language
        templates[lang].to = obj.email
        templates[lang].send({"name": obj.get_full_name()})

    def response_change(self, request, obj):
        if "_accept" in request.POST:
            if request.user.has_perm("members.can_accept_or_reject"):
                if self.send_accept_email(request, obj):
                    obj.is_active = True
                    obj.save()
            else:
                raise PermissionDenied(_("You don't have permission to accept a user"))
            return HttpResponseRedirect(".")
        if "_reject" in request.POST:
            if not request.user.has_perm("members.can_accept_or_reject"):
                raise PermissionDenied(_("You don't have permission to accept a user"))
            if obj.is_active:
                raise ValidationError(
                    _("You can't deny a person who is already active")
                )
            obj.delete()
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["show_accept_reject_buttons"] = request.user.has_perm(
            "members.can_accept_or_reject"
        )
        return super(UserAdmin, self).change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )

    def send_password_email(self, request, queryset):
        current_site = get_current_site(request)
        domain = current_site.domain
        use_https = "https" if request.is_secure() else "http"
        base = f"{use_https}://{domain}"

        token_generator = AccountActivationTokenGenerator()

        templates = {}
        success = True
        for lang, display in settings.LANGUAGES:
            t = Configuration.get_mail_template("activate_account_" + lang)
            if t:
                templates[lang] = t
            elif Configuration.objects.filter(
                process="activate_account_" + lang
            ).exists():
                messages.error(
                    request,
                    (
                        _(
                            "No email template has been attached to the %s configuration, you have to create one first"
                        )
                        % lang
                    ),
                )
                success = False
            else:
                Configuration.objects.create(
                    process="activate_account_" + lang,
                    description="""This configuration is used to send the account activation emails for imported users.
                    
                    You can use the following variables:
                    {name}: the name of the user
                    {link}: the link where the user can activate your account
                    """,
                )
                messages.error(
                    request,
                    (
                        _(
                            "No configuration exists for %s and has been created. You do have to add a template yourself"
                        )
                        % lang
                    ),
                )
                success = False
        if not success:
            return

        for user in queryset:
            link = base + reverse(
                "activate-account",
                kwargs={
                    "uidb64": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": token_generator.make_token(user),
                },
            )

            lang = user.member.preferred_language
            templates[lang].to = user.email
            templates[lang].send({"name": user.get_full_name(), "link": link})

            user.is_active = True
            user.set_unusable_password()
            user.save()


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(OtherClub)
class OtherClubAdmin(admin.ModelAdmin):
    pass



