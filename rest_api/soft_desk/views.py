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
from soft_desk.permissions import IsAuthenticatedOwnerOrContributor
from soft_desk.serializers import CommentSerializer, ContributorSerializer, IssueSerializer, ProjectSerializer, UserSerializer



class UserSignUp(APIView):
    # Allow any user (authenticated or not) to access this url
    permission_classes = (AllowAny,)

    def post(self, request):
        user = request.data
        serializer = UserSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserLogin(APIView):
    # Allow any user (authenticated or not) to access this url
    permission_classes = (AllowAny,)

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


class ProjectList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProjectSerializer

    def get_queryset(self):
        """
        Liste des projets créés par l'utilisateur ou des projets sur lesquels l'utilisateur est contributeur
        """
        list_project_id = [q['project_id'] for q in Contributor.objects.filter(user=self.request.user).values('project_id')]
        return Project.objects.filter(Q(author_user=self.request.user) | Q(project_id__in=list_project_id))

    def perform_create(self, serializer):
        serializer.save(author_user=self.request.user)


class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly,)
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def patch(self, request, *args, **kwargs):
        res = {
            'detail': 'Méthode « PATCH » non autorisée.'}
        return Response(res, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ContributorList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = ContributorSerializer

    def get_queryset(self):
        the_project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        return Contributor.objects.filter(project=the_project)

    def perform_create(self, serializer):
        the_project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        if self.request.user == the_project.author_user:
            serializer.save()
        else:
            res = {'detail': 'Seul le créateur du projet peut ajouter des contributeurs sur le projet'}
            return Response(res, status=status.HTTP_403_FORBIDDEN)


class ContributorDelete(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly,)
    serializer_class = ContributorSerializer

    def get_queryset(self):
        return get_object_or_404(Contributor,
                        project_project_id=self.kwargs['project_id'],
                        user_user_id=self.kwargs['user_id'])

    def perform_destroy(self, instance):
        if instance.user_id == self.request.user.user_id:
            instance.delete()
        else:
            res = {'detail': 'Seul le créateur du projet peut supprimer des contributeurs sur le projet'}
            return Response(res, status=status.HTTP_403_FORBIDDEN)


class IssueList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = IssueSerializer

    def get_queryset(self):
        the_project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        return Issue.objects.filter(project=the_project)

    def perform_create(self, serializer):
        serializer.save(author_user_id=self.request.user.user_id)


class IssueUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly,)
    #queryset = Issue.objects.all()
    serializer_class = IssueSerializer

    def get_queryset(self):
        return get_object_or_404(Issue, pk=self.kwargs['issue_id'])

    def get(self, request, *args, **kwargs):
        res = {
            'detail': 'Méthode « GET » non autorisée.'}
        return Response(res, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        res = {
            'detail': 'Méthode « PATCH » non autorisée.'}
        return Response(res, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CommentList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CommentSerializer

    def get_queryset(self):
        the_issue = get_object_or_404(Issue, pk=self.kwargs['issue_id'])
        return Comment.objects.filter(issue=the_issue)

    def perform_create(self, serializer):
        serializer.save(author_user_id=self.request.user.user_id)


class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly,)
    serializer_class = CommentSerializer

    def get_queryset(self):
        return get_object_or_404(Comment, pk=self.kwargs['comment_id'])

    def patch(self, request, *args, **kwargs):
        res = {
            'detail': 'Méthode « PATCH » non autorisée.'}
        return Response(res, status=status.HTTP_405_METHOD_NOT_ALLOWED)


""" DEBUT VIEWSETS """


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
    # Allow any user (authenticated or not) to access this url
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
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly,)
    serializer_class = ProjectSerializer

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
    permission_classes = (IsAuthenticatedOwnerOrContributor,)
    serializer_class = ContributorSerializer

    def get_queryset(self):
        the_project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        return Contributor.objects.filter(project=the_project).order_by('user_id')

    def create(self, request, *args, **kwargs):
        the_project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        data_project_id = request.data['project_id']
        if the_project.project_id != data_project_id:
            res = {'detail': 'Operation illicite project_id dans l\'URL (' + str(the_project.project_id) + ') différent de celui passé dans l\'objet JSON (' + str(data_project_id) + ')'}
            return Response(res, status=status.HTTP_403_FORBIDDEN)
        elif self.request.user != the_project.author_user:
            res = {'detail': 'Seul le créateur du projet peut ajouter un contributeur au projet'}
            return Response(res, status=status.HTTP_403_FORBIDDEN)
        else:
            return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        the_project = get_object_or_404(Project, pk=self.kwargs['pk'])
        if self.request.user != the_project.author_user:
            res = {'detail': 'L\'utilisateur n\'est pas habilité à effectuer cette opération'}
            return Response(res, status=status.HTTP_403_FORBIDDEN)
        else:
            return super().destroy(request, *args, **kwargs)


class IssueViewSet(mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly,)
    serializer_class = IssueSerializer

    def get_queryset(self):
        the_project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        return Issue.objects.filter(project=the_project).order_by('issue_id')

    def create(self, request, *args, **kwargs):
        the_project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        data_project_id = request.data['project_id']
        if the_project.project_id != data_project_id:
            res = {'detail': 'Operation illicite project_id dans l\'URL (' + str(the_project.project_id) + ') différent de celui passé dans l\'objet JSON (' + str(data_project_id) + ')'}
            return Response(res, status=status.HTTP_403_FORBIDDEN)
        else:
            return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        the_issue = get_object_or_404(Issue, pk=self.kwargs['pk'])
        if self.request.user != the_issue.author_user:
            res = {'detail': 'L\'utilisateur n\'est pas habilité à effectuer cette opération'}
            return Response(res, status=status.HTTP_403_FORBIDDEN)
        else:
            return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        the_issue = get_object_or_404(Issue, pk=self.kwargs['pk'])
        if self.request.user != the_issue.author_user:
            res = {'detail': 'L\'utilisateur n\'est pas habilité à effectuer cette opération'}
            return Response(res, status=status.HTTP_403_FORBIDDEN)
        else:
            return super().update(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly,)
    serializer_class = IssueSerializer

    def get_queryset(self):
        the_issue = get_object_or_404(Project, pk=self.kwargs['issue_pk'])
        return Comment.objects.filter(issue=the_issue).order_by('comment_id')


    def create(self, request, *args, **kwargs):
        the_project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        data_project_id = request.data['project_id']
        the_issue = get_object_or_404(Issue, pk=self.kwargs['issue_pk'])
        data_issue_id = request.data['issue_id']
        if the_project.project_id != data_project_id:
            res = {'detail': 'Operation illicite project_id dans l\'URL (' + str(the_project.project_id) + ') différent de celui passé dans l\'objet JSON (' + str(data_project_id) + ')'}
            return Response(res, status=status.HTTP_403_FORBIDDEN)
        elif the_issue.issue_id != data_issue_id:
            res = {'detail': 'Operation illicite issue_id dans l\'URL (' + str(the_issue.issue_id) + ') différent de celui passé dans l\'objet JSON (' + str(data_issue_id) + ')'}
            return Response(res, status=status.HTTP_403_FORBIDDEN)
        else:
            return super().create(request, *args, **kwargs)
