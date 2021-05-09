from django.shortcuts import get_object_or_404
from rest_framework import permissions
from soft_desk.models import Contributor, Project


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
        user_is_authenticated = bool(request.user and request.user.is_authenticated)
        the_project = get_object_or_404(Project, pk=view.kwargs['project_pk'])
        set_of_user_id = {q['user_id'] for q in Contributor.objects.filter(project=the_project).values('user_id')}
        user_is_contributor = bool(request.user.user_id in set_of_user_id)
        if isinstance(view, soft_desk.views.ContributorViewSet):
            the_object = the_project
        elif isinstance(view, soft_desk.views.IssueViewSet):
            if 'pk' in views.kwargs:
                the_object = get_object_or_404(Issue, pk=view.kwargs['pk'])
            else:
                the_object = the_project
        elif isinstance(view, soft_desk.views.CommentViewSet):
            if 'pk' in views.kwargs:
                the_object = get_object_or_404(Comment, pk=view.kwargs['pk'])
            else:
                the_object = the_project

        user_is_owner = bool(the_object.author_user == request.user)

        if request.method in permissions.SAFE_METHODS:
            return bool(user_is_authenticated and (user_is_contributor or user_is_owner))
        else:
            return bool(user_is_authenticated and user_is_owner)


class OwnerOrContributor(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    print("IsOwnerOrContributor")


    def has_object_permission(self, request, view, obj):
        print("in has_object_permission")
        print("self :", self)
        print("request :", request)
        print("view :", view)
        print("obj :", obj)
        user_is_contributor = False
        user_is_owner = False
        the_project = None

        if isinstance(obj, Comment):
            print("Instance Comment :", obj)
            the_project = obj.issue.project

        if isinstance(obj, Contributor) or isinstance(obj, Issue):
            print("Instance :", obj)
            the_project = obj.project

        set_of_user_id = {q['user_id'] for q in Contributor.objects.filter(project=the_project).values('user_id')}
        print("set_of_user_id :", set_of_user_id)
        user_is_contributor = (request.user.user_id in set_of_user_id)

        print("user_is_contributor :", user_is_contributor)

        if hasattr(obj, 'author_user'):
            user_is_owner = (obj.author_user == request.user)

        print("user_is_owner :", user_is_owner)

        if request.method in permissions.SAFE_METHODS:
            return user_is_contributor or user_is_owner

        return user_is_owner
