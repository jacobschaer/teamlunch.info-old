from django.contrib import admin
from .models import Team, TeamMember

class TeamMemberInline(admin.StackedInline):
    model = TeamMember
    extra = 1


class TeamAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name']}),
    ]
    inlines = [TeamMemberInline]

# Register your models here.
admin.site.register(Team, TeamAdmin)