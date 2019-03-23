from django.contrib import admin

from .models import Skill, Project, User, Position, Participant

admin.site.register(Skill)
admin.site.register(Project)
admin.site.register(User)
admin.site.register(Position)
admin.site.register(Participant)
