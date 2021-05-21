"""rest_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include

from rest_framework_nested.routers import DefaultRouter,  NestedSimpleRouter
from soft_desk import views

router = DefaultRouter()
router.register(r'login', views.UserLoginViewSet, basename='login')
router.register(r'signup', views.UserSignUpViewSet, basename='signup')

project_router = DefaultRouter()
project_router.register(r'projects', views.ProjectViewSet, basename='projects')
# generates:
# /projects/
# /projects/{pk}/

contributor_router = NestedSimpleRouter(project_router,
                                        r'projects',
                                        lookup='project')
contributor_router.register(r'users', views.ContributorViewSet,
                            basename='contributors')
# generates:
# /projects/{project_pk}/users/
# /projects/{project_pk}/users/{pk}/

issue_router = NestedSimpleRouter(project_router,
                                  r'projects', lookup='project')
issue_router.register(r'issues', views.IssueViewSet, basename='issues')
# generates:
# /projects/{project_pk}/issues/
# /projects/{project_pk}/issues/{pk}/

comment_router = NestedSimpleRouter(issue_router, r'issues', lookup='issue')
comment_router.register(r'comments', views.CommentViewSet, basename='comments')
# generates:
# /projects/{project_pk}/issues/{issue_pk}/comments/
# /projects/{project_pk}/issues/{issue_pk}/comments/{pk}/

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('', include(project_router.urls)),
    path('', include(contributor_router.urls)),
    path('', include(issue_router.urls)),
    path('', include(comment_router.urls)),
]
