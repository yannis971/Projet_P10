from django.contrib.auth.signals import user_logged_in
from django.db.models import Q
from django.shortcuts import get_object_or_404


from rest_framework import generics
from rest_framework import mixins
from rest_framework.permissions import  AllowAny, IsAuthenticated
from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework import status

from rest_framework_jwt.settings import api_settings

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

#Debut import pour viewsets
from rest_framework import viewsets
#Fin import pour viewsets

from soft_desk.models import Comment, Contributor, Issue, Project, User
from soft_desk.permissions import IsOwnerOrReadOnly
from soft_desk.permissions import IsAuthenticatedOwner
from soft_desk.permissions import IsAuthenticatedOwnerOrContributor
from soft_desk.permissions import ActionNotAllowed
from soft_desk.serializers import CommentSerializer, ContributorSerializer, IssueSerializer, ProjectSerializer, UserSerializer


class UserSignUpViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = (AllowAny,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request):
        user = request.data
        serializer = UserSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserLoginViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
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
            return Response(res)

    def list(self, request, *args, **kwargs):
        res = {
            'detail': 'Méthode « GET » non autorisée.'}
        return Response(res, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list' or self.action == 'create':
            permission_classes = (IsAuthenticated, IsOwnerOrReadOnly,)
        elif self.action == 'retrieve':
            permission_classes = (IsAuthenticatedOwnerOrContributor,)
        elif self.action == 'update' or self.action == 'destroy':
            permission_classes = (IsAuthenticatedOwner,)
        else:
            permission_classes = (ActionNotAllowed,)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Liste des projets créés par l'utilisateur ou des projets sur lesquels l'utilisateur est contributeur
        """
        list_project_id = [q['project_id'] for q in Contributor.objects.filter(user=self.request.user).values('project_id')]
        return Project.objects.filter(Q(author_user=self.request.user) | Q(project_id__in=list_project_id)).order_by('project_id')

    def perform_create(self, serializer):
        serializer.save(author_user=self.request.user)


class ContributorViewSet(mixins.CreateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    serializer_class = ContributorSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list':
            permission_classes = (IsAuthenticatedOwnerOrContributor,)
        else:
            permission_classes = (IsAuthenticatedOwner,)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        the_project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        return Contributor.objects.filter(project=the_project).order_by('user_id')

    def perform_create(self, serializer):
        the_user = get_object_or_404(User, pk=serializer._kwargs['data']['user_id'])
        the_project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        serializer.save(user=the_user, project=the_project)


class IssueViewSet(mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    serializer_class = IssueSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list' or self.action == 'create':
            permission_classes = (IsAuthenticatedOwnerOrContributor,)
        elif self.action == 'update' or self.action == 'destroy':
            permission_classes = (IsAuthenticatedOwner,)
        else:
            permission_classes = (ActionNotAllowed,)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        the_project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        return Issue.objects.filter(project=the_project).order_by('issue_id')

    def perform_create(self, serializer):
        the_assignee_user = get_object_or_404(User, pk=serializer._kwargs['data']['assignee_user_id'])
        the_project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        the_author_user = self.request.user
        serializer.save(assignee_user=the_assignee_user, author_user=the_author_user, project=the_project)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list' or self.action == 'create' or self.action == 'retrieve':
            permission_classes = (IsAuthenticatedOwnerOrContributor,)
        elif self.action == 'update' or self.action == 'destroy':
            permission_classes = (IsAuthenticatedOwner,)
        else:
            permission_classes = (ActionNotAllowed,)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        the_issue = get_object_or_404(Issue, pk=self.kwargs['issue_pk'])
        return Comment.objects.filter(issue=the_issue).order_by('comment_id')

    def perform_create(self, serializer):
        the_issue = get_object_or_404(Issue, pk=self.kwargs['issue_pk'])
        the_author_user = self.request.user
        serializer.save(author_user=the_author_user, issue=the_issue)
