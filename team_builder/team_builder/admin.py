from django.contrib import admin

from .models import Participant, Position, Project, Skill, User

admin.site.register(Skill)
admin.site.register(Project)
admin.site.register(User)
admin.site.register(Position)
admin.site.register(Participant)
