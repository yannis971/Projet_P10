
from django.urls import path

from soft_desk import views

app_name = 'soft_desk'

urlpatterns = [
    path('signup/', views.UserSignUp.as_view(), name='user-sign-up'),
    path('login/', views.UserLogin.as_view(), name='user-login'),
    path('projects/', views.ProjectList.as_view(), name='project-list'),
    path('projects/<int:project_id>/', views.ProjectDetail.as_view(), name='project-detail'),
    path('projects/<int:project_id>/users/', views.ContributorList.as_view(), name='contributor-list'),
]
