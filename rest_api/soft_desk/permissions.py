from django.shortcuts import get_object_or_404
from rest_framework import permissions
from soft_desk.models import Contributor, Comment, Project, Issue, Project


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        if hasattr(obj, 'author_user'):
            return obj.author_user == request.user
        else:
            return False


class IsAuthenticatedOwnerOrContributor(permissions.BasePermission):
    """
    The request is authenticated as a user, or is a read-only request.
    """

    def has_permission(self, request, view):
        from soft_desk.views import CommentViewSet, ContributorViewSet, IssueViewSet, ProjectViewSet
        user_is_authenticated = bool(request.user and request.user.is_authenticated)
        if isinstance(view, ProjectViewSet):
            the_project = get_object_or_404(Project, pk=view.kwargs['pk'])
        else:
            the_project = get_object_or_404(Project, pk=view.kwargs['project_pk'])
        set_of_user_id = {q['user_id'] for q in Contributor.objects.filter(project=the_project).values('user_id')}
        user_is_contributor = bool(request.user.user_id in set_of_user_id)
        the_object = the_project

        if isinstance(view, IssueViewSet):
            if 'pk' in view.kwargs:
                the_object = get_object_or_404(Issue, pk=view.kwargs['pk'])
            else:
                the_object = the_project
        elif isinstance(view, CommentViewSet):
            if 'pk' in view.kwargs:
                the_object = get_object_or_404(Comment, pk=view.kwargs['pk'])
            else:
                the_object = the_project

        user_is_owner = bool(the_object.author_user == request.user)
        print("request.method :", request.method)
        print("user_is_authenticated :", user_is_authenticated)
        print("user_is_owner :", user_is_owner)
        print("user_is_contributor :", user_is_contributor)

        return bool(user_is_authenticated and (user_is_contributor or user_is_owner))



class IsAuthenticatedOwner(permissions.BasePermission):
    """
    The request is authenticated as a user, or is a read-only request.
    """

    def has_permission(self, request, view):
        from soft_desk.views import CommentViewSet, ContributorViewSet, IssueViewSet, ProjectViewSet
        user_is_authenticated = bool(request.user and request.user.is_authenticated)
        the_project = get_object_or_404(Project, pk=view.kwargs['project_pk'])
        if isinstance(view, ContributorViewSet):
            the_object = the_project
        elif isinstance(view, IssueViewSet):
            if 'pk' in view.kwargs:
                the_object = get_object_or_404(Issue, pk=view.kwargs['pk'])
            else:
                the_object = the_project
        elif isinstance(view, CommentViewSet):
            if 'pk' in view.kwargs:
                the_object = get_object_or_404(Comment, pk=view.kwargs['pk'])
            else:
                the_object = the_project
        else:
            the_object = the_project

        user_is_owner = bool(the_object.author_user == request.user)

        return bool(user_is_authenticated and user_is_owner)
