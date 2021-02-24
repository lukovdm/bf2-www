from django.contrib import admin

from .models import Member, OtherClub


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    pass

@admin.register(OtherClub)
class OtherClubAdmin(admin.ModelAdmin):
    pass
