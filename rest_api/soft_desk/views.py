from django.contrib.auth.signals import user_logged_in
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

            #user = User.objects.get(email=email, password=password)
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
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

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
    # Allow any user (authenticated or not) to access this url
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

    def get_extra_actions():
        return ['get',]

    def post(self, request):
        try:
            email = request.data['email']
            password = request.data['password']

            user = User.objects.get(email=email, password=password)
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


class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def perform_create(self, serializer):
        serializer.save(author_user=self.request.user)


class ProjectDetailViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
