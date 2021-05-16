from django.contrib.auth.signals import user_logged_in
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.db.utils import IntegrityError

from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets

from rest_framework.permissions import  AllowAny
from rest_framework.response import Response

from rest_framework_jwt.settings import api_settings

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


from soft_desk.models import Comment, Contributor, Issue, Project, User
from soft_desk.permissions import CommentPermission
from soft_desk.permissions import ContributorPermission
from soft_desk.permissions import IssuePermission
from soft_desk.permissions import ProjectPermission
from soft_desk.serializers import CommentSerializer, ContributorSerializer, IssueSerializer, ProjectSerializer, UserSerializer


class UserSignUpViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = (AllowAny,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        serializer.save()


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
            return Response(res, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        res = {
            'detail': 'Méthode « GET » non autorisée.'}
        return Response(res, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = (ProjectPermission,)

    def get_queryset(self):
        """
        Liste des projets créés par l'utilisateur ou des projets sur lesquels l'utilisateur est contributeur
        """
        if self.action == 'list':
            Project.objects.all()
            list_project_id = [q['project_id'] for q in Contributor.objects.filter(user=self.request.user).values('project_id')]
            return Project.objects.filter(Q(author_user=self.request.user) | Q(project_id__in=list_project_id)).order_by('project_id')
        else:
            return Project.objects.all()

    def perform_create(self, serializer):
        serializer.save(author_user=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data_to_update = request.data
        if 'title' not in data_to_update:
            data_to_update['title'] = instance.title
        serializer = self.get_serializer(instance, data=data_to_update, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        res = {
            'detail': 'Méthode « PATCH » non autorisée.'}
        return Response(res, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ContributorViewSet(mixins.CreateModelMixin,
                         mixins.DestroyModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    serializer_class = ContributorSerializer
    permission_classes = (ContributorPermission,)

    def get_queryset(self):
        the_project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        return Contributor.objects.filter(project=the_project).order_by('user_id')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except IntegrityError:
            res = {'this contributor already exists'}
            return Response(res, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        the_user = get_object_or_404(User, pk=serializer._kwargs['data']['user_id'])
        the_project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        serializer.save(user=the_user, project=the_project)

    def destroy(self, request, *args, **kwargs):
        the_user = get_object_or_404(User, pk=self.kwargs['pk'])
        the_project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        instance = Contributor.objects.get(project=the_project, user=the_user)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class IssueViewSet(mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    serializer_class = IssueSerializer
    permission_classes = (IssuePermission,)

    def get_queryset(self):
        the_project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        return Issue.objects.filter(project=the_project).order_by('issue_id')

    def perform_create(self, serializer):
        the_assignee_user = get_object_or_404(User, pk=serializer._kwargs['data']['assignee_user_id'])
        the_project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        the_author_user = self.request.user
        serializer.save(assignee_user=the_assignee_user, author_user=the_author_user, project=the_project)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data_to_update = request.data
        if 'title' not in data_to_update:
            data_to_update['title'] = instance.title
        serializer = self.get_serializer(instance, data=data_to_update, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        res = {
            'detail': 'Méthode « PATCH » non autorisée.'}
        return Response(res, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CommentViewSet(viewsets.ModelViewSet):
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
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data_to_update = request.data
        if 'description' not in data_to_update:
            data_to_update['description'] = instance.title
        serializer = self.get_serializer(instance, data=data_to_update, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        res = {
            'detail': 'Méthode « PATCH » non autorisée.'}
        return Response(res, status=status.HTTP_405_METHOD_NOT_ALLOWED)