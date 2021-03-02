from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.dateparse import parse_date
from import_export import resources
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportMixin

from .models import Member, OtherClub


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
            "member__other_club"
        )

    def init_instance(self, row=None):
        print(row)
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


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(OtherClub)
class OtherClubAdmin(admin.ModelAdmin):
    pass
