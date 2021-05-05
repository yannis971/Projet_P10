from django.contrib import admin


from soft_desk.models import Comment
from soft_desk.models import Contributor
from soft_desk.models import Issue
from soft_desk.models import Project
from soft_desk.models import User

admin.site.register(Comment)
admin.site.register(Contributor)
admin.site.register(Issue)
admin.site.register(Project)
admin.site.register(User)
