from django.contrib.auth.signals import user_logged_in
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.db.utils import IntegrityError

from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets

from rest_framework.exceptions import NotFound
from rest_framework.exceptions import ValidationError

from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from rest_framework_jwt.settings import api_settings

from soft_desk.mixins import CustomUpdateModelMixin
from soft_desk.models import Comment, Contributor, Issue, Project, User
from soft_desk.permissions import CommentPermission
from soft_desk.permissions import ContributorPermission
from soft_desk.permissions import IssuePermission
from soft_desk.permissions import ProjectPermission
from soft_desk.serializers import CommentSerializer, ContributorSerializer, IssueSerializer, ProjectSerializer, UserSerializer

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class UserSignUpViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    class UserSignUpViewSet manages the following endpoint :
    /signup/
    """
    permission_classes = (AllowAny,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        serializer.save()


class UserLoginViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    class UserLoginViewSet manages the following endpoint :
    /login/
    """
    permission_classes = (AllowAny,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request):
        try:
            email = request.data['email']
            password = request.data['password']
            user = get_object_or_404(User, email=email, password=password)
            if user:
                try:
                    payload = jwt_payload_handler(user)
                    token = jwt_encode_handler(payload)
                    user_details = {}
                    user_details['name'] = "%s %s" % (
                        user.first_name, user.last_name)
                    user_details['token'] = token
                    user_logged_in.send(sender=user.__class__,
                                        request=request, user=user)
                    return Response(user_details, status=status.HTTP_200_OK)
                except Exception as e:
                    raise e
            else:
                res = {
                    'error': 'can not authenticate with the given credentials or the account has been deactivated'}
                return Response(res, status=status.HTTP_403_FORBIDDEN)
        except KeyError:
            res = {'error': 'please provide a email and a password'}
            return Response(res, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        res = {
            'detail': 'Méthode « GET » non autorisée.'}
        return Response(res, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ProjectViewSet(CustomUpdateModelMixin, viewsets.ModelViewSet):
    """
    class ProjectViewSet manages the following endpoints :
    /projects/
    /projects/{pk}/
    """
    serializer_class = ProjectSerializer
    permission_classes = (ProjectPermission,)

    def get_queryset(self):
        if self.action == 'list':
            Project.objects.all()
            list_project_id = [q['project_id'] for q in Contributor.objects.filter(user=self.request.user).values('project_id')]
            return Project.objects.filter(Q(author_user=self.request.user) | Q(project_id__in=list_project_id)).order_by('project_id')
        else:
            return Project.objects.all()

    def perform_create(self, serializer):
        serializer.save(author_user=self.request.user)

    def update(self, request, *args, **kwargs):
        return self.custom_update(request, 'title', **kwargs)


class ContributorViewSet(mixins.CreateModelMixin,
                         mixins.DestroyModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    """
    class ContributorViewSet manages the following endpoints :
    /projects/{project_pk}/users/
    /projects/{project_pk}/users/{pk}/
    """
    serializer_class = ContributorSerializer
    permission_classes = (ContributorPermission,)

    def get_queryset(self):
        the_project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        return Contributor.objects.filter(project=the_project).order_by('user_id')

    def get_object(self):
        the_user = get_object_or_404(User, pk=self.kwargs['pk'])
        the_project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        try:
            obj = Contributor.objects.get(project=the_project, user=the_user)
        except Contributor.DoesNotExist:
            raise NotFound("The contributor does not exist")
        else:
            return obj

    def perform_create(self, serializer):
        the_user = get_object_or_404(User, pk=serializer._kwargs['data']['user_id'])
        the_project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        try:
            serializer.save(user=the_user, project=the_project)
        except IntegrityError:
            raise ValidationError("this contributor already exists")


class IssueViewSet(mixins.CreateModelMixin,
                   CustomUpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    """
    class IssueViewSet manages the following endpoints :
    /projects/{project_pk}/issues/
    /projects/{project_pk}/issues/{pk}/
    """
    serializer_class = IssueSerializer
    permission_classes = (IssuePermission,)

    def get_queryset(self):
        the_project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        return Issue.objects.filter(project=the_project).order_by('issue_id')

    def perform_create(self, serializer):
        the_assignee_user = get_object_or_404(User, pk=serializer._kwargs['data']['assignee_user_id'])
        the_project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        the_author_user = self.request.user
        try:
            serializer.save(assignee_user=the_assignee_user, author_user=the_author_user, project=the_project)
        except IntegrityError:
            raise ValidationError("this issue already exists")

    def update(self, request, *args, **kwargs):
        return self.custom_update(request, 'title', **kwargs)


class CommentViewSet(CustomUpdateModelMixin, viewsets.ModelViewSet):
    """
    class IssueViewSet manages the following endpoints :
    /projects/{project_pk}/issues/{issue_pk}/comments/
    /projects/{project_pk}/issues/{issue_pk}/comments/{pk}/
    """
    serializer_class = CommentSerializer
    permission_classes = (CommentPermission,)

    def get_queryset(self):
        the_issue = get_object_or_404(Issue, pk=self.kwargs['issue_pk'])
        return Comment.objects.filter(issue=the_issue).order_by('comment_id')

    def perform_create(self, serializer):
        the_issue = get_object_or_404(Issue, pk=self.kwargs['issue_pk'])
        the_author_user = self.request.user
        serializer.save(author_user=the_author_user, issue=the_issue)

    def update(self, request, *args, **kwargs):
        return self.custom_update(request, 'description', **kwargs)
