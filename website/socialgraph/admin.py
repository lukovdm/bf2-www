from django.contrib import admin

from socialgraph.models import Relation


@admin.register(Relation)
class RelationAdmin(admin.ModelAdmin):
    pass
