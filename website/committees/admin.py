from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from committees.models import Committee, CommitteeMembership


class CommitteeMembershipInline(admin.TabularInline):
    model = CommitteeMembership
    can_delete = False


@admin.register(Committee)
class CommitteeAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "active_member_count", "active", "is_staff", "show_in_achievements")
    list_filter = ("active", "is_staff", "image")

    inlines = (CommitteeMembershipInline,)
    fields = (
        ("name_en", "name_nl"),
        "image",
        "email",
        ("show_members", "active"),
        "is_staff",
        "perm_group",
    )

    def formfield_for_dbfield(self, db_field, *args, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, *args, **kwargs)

        if db_field.attname == "perm_group_id":
            formfield.widget.can_delete_related = False
            formfield.widget.can_add_related = False

        return formfield

    @admin.display(description=_("Active members"))
    def active_member_count(self, obj: Committee):
        return obj.committeemembership_set.exclude(until__lte=timezone.now()).count()
