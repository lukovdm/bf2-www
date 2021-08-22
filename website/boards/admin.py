from django.contrib import admin

from boards.models import Board, BoardMembership


class BoardMembershipInline(admin.StackedInline):
    model = BoardMembership

    def get_extra(self, request, obj=None, **kwargs):
        extra = 4
        if obj:
            return extra - obj.boardmembership_set.count()
        return extra


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    inlines = (BoardMembershipInline,)
