from django.contrib import admin


from soft_desk.models import Project
from soft_desk.models import User

admin.site.register(User)
admin.site.register(Project)
