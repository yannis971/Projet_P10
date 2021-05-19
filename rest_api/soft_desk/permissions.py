from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework import exceptions

from soft_desk.models import Contributor, Comment, Issue, Project


class IsAuthenticatedOwnerOrContributor(permissions.BasePermission):
    """
    The request is authenticated as a user, or is a read-only request.
    """

    def has_permission(self, request, view):
        from soft_desk.views import CommentViewSet, IssueViewSet, ProjectViewSet
        user_is_authenticated = bool(request.user and request.user.is_authenticated)
        if isinstance(view, ProjectViewSet):
            the_project = get_object_or_404(Project, pk=view.kwargs['pk'])
        else:
            the_project = get_object_or_404(Project, pk=view.kwargs['project_pk'])
        user_is_contributor = request.user.is_contributor(the_project)
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
        return bool(user_is_authenticated and (user_is_contributor or user_is_owner))

    def has_object_permission(self, request, view, obj):
        user_is_authenticated = bool(request.user and request.user.is_authenticated)
        if isinstance(obj, Contributor) or isinstance(obj, Issue):
            the_project = obj.project
        elif isinstance(obj, Comment):
            the_project = obj.issue.project
        else:
            the_project = obj
        user_is_contributor = request.user.is_contributor(the_project)
        if isinstance(obj, Contributor):
            the_object = the_project
        else:
            the_object = obj
        user_is_owner = bool(the_object.author_user == request.user)
        return bool(user_is_authenticated and (user_is_contributor or user_is_owner))


class IsAuthenticatedOwner(permissions.BasePermission):
    """
    The request is authenticated as a user
    """

    def has_permission(self, request, view):
        from soft_desk.views import ProjectViewSet
        user_is_authenticated = bool(request.user and request.user.is_authenticated)
        for (attr, value) in view.__dict__.items():
            print(attr, ":", value)
        if isinstance(view, ProjectViewSet):
            the_project = get_object_or_404(Project, pk=view.kwargs['pk'])
        else:
            the_project = get_object_or_404(Project, pk=view.kwargs['project_pk'])
        the_object = the_project
        user_is_owner = bool(the_object.author_user == request.user)
        return bool(user_is_authenticated and user_is_owner)

    def has_object_permission(self, request, view, obj):
        user_is_authenticated = bool(request.user and request.user.is_authenticated)
        if isinstance(obj, Contributor):
            the_object = obj.project
        else:
            the_object = obj
        user_is_owner = bool(the_object.author_user == request.user)
        return bool(user_is_authenticated and user_is_owner)


class GenericModelPermission(permissions.BasePermission):
    def __init__(self, model):
        super()
        self.model = model
        self.permissions_view_map = {}
        self.permissions_object_map = {}

    def has_permission(self, request, view):
        if 'pk' in view.kwargs:
            obj = view.get_object()
            return self.has_object_permission(request, view, obj)
        elif view.action in self.permissions_view_map:
            perms = {f().has_permission(request, view) for f in self.permissions_view_map[view.action]}
            if False in perms:
                return False
            else:
                return True
        else:
            raise exceptions.MethodNotAllowed(request.method)

    def has_object_permission(self, request, view, obj):
        if view.action in self.permissions_object_map:
            perms = {f().has_object_permission(request, view, obj) for f in self.permissions_object_map[view.action]}
            if False in perms:
                return False
            else:
                return True
        else:
            raise exceptions.MethodNotAllowed(request.method)


class ProjectPermission(GenericModelPermission):
    def __init__(self):
        super().__init__(model=Project)
        self.permissions_view_map['list'] = (IsAuthenticated,)
        self.permissions_view_map['create'] = (IsAuthenticated,)
        self.permissions_object_map['retrieve'] = (IsAuthenticatedOwnerOrContributor,)
        self.permissions_object_map['update'] = (IsAuthenticatedOwner,)
        self.permissions_object_map['destroy'] = (IsAuthenticatedOwner,)


class ContributorPermission(GenericModelPermission):
    def __init__(self):
        super().__init__(model=Contributor)
        self.permissions_view_map['list'] = (IsAuthenticatedOwnerOrContributor,)
        self.permissions_view_map['create'] = (IsAuthenticatedOwner,)
        self.permissions_object_map['destroy'] = (IsAuthenticatedOwner,)


class IssuePermission(GenericModelPermission):
    def __init__(self):
        super().__init__(model=Issue)
        self.permissions_view_map['list'] = (IsAuthenticatedOwnerOrContributor,)
        self.permissions_view_map['create'] = (IsAuthenticatedOwnerOrContributor,)
        self.permissions_object_map['update'] = (IsAuthenticatedOwner,)
        self.permissions_object_map['destroy'] = (IsAuthenticatedOwner,)


class CommentPermission(GenericModelPermission):
    def __init__(self):
        super().__init__(model=Comment)
        self.permissions_view_map['list'] = (IsAuthenticatedOwnerOrContributor,)
        self.permissions_view_map['create'] = (IsAuthenticatedOwnerOrContributor,)
        self.permissions_object_map['retrieve'] = (IsAuthenticatedOwnerOrContributor,)
        self.permissions_object_map['update'] = (IsAuthenticatedOwner,)
        self.permissions_object_map['destroy'] = (IsAuthenticatedOwner,)
