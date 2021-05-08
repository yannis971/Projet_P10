
from django.urls import path, include
#from rest_framework.routers import DefaultRouter

from soft_desk import views

urlpatterns = [
    path('signup/', views.UserSignUp.as_view(), name='user-sign-up'),
    path('login/', views.UserLogin.as_view(), name='user-login'),
    path('projects/', views.ProjectList.as_view(), name='project-list'),
    path('projects/<int:pk>/', views.ProjectDetail.as_view(), name='project-detail'),
    path('projects/<int:project_id>/users/', views.ContributorList.as_view(), name='contributor-list'),
    path('projects/<int:project_id>/users/<int:user_id>', views.ContributorDelete.as_view(), name='contributor-delete'),
    path('projects/<int:project_id>/issues/', views.IssueList.as_view(), name='issue-list'),
    path('projects/<int:project_id>/issues/<int:issue_id>', views.IssueUpdateDestroy.as_view(), name='issue-update-delete'),
    path('projects/<int:project_id>/issues/<int:issue_id>>/comments/', views.CommentList.as_view(), name='comment-list'),
    path('projects/<int:project_id>/issues/<int:issue_id>>/comments/<int:comment_id>', views.CommentDetail.as_view(), name='comment-detail'),
]

"""
router = DefaultRouter()
router.register(r'signup/', views.UserSignUpViewSet)
router.register(r'login/', views.UserLoginViewSet)
urlpatterns = [
    path('', include(router.urls)),
]
router.register(r'projects/$', views.ProjectList.as_view())
router.register(r'projects/<int:pk>/', views.ProjectDetail.as_view())
router.register(r'projects/<int:project_id>/users/', views.ContributorList.as_view())
router.register(r'projects/<int:project_id>/users/<int:user_id>', views.ContributorDelete.as_view())
router.register(r'projects/<int:project_id>/issues/', views.IssueList.as_view())
router.register(r'projects/<int:project_id>/issues/<int:issue_id>', views.IssueUpdateDestroy.as_view())
router.register(r'projects/<int:project_id>/issues/<int:issue_id>>/comments/', views.CommentList.as_view())
router.register(r'projects/<int:project_id>/issues/<int:issue_id>>/comments/<int:comment_id>', views.CommentDetail.as_view())
"""
# The API URLs are now determined automatically by the router.
