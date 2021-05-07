from django.contrib.auth.signals import user_logged_in
from django_filters.rest_framework import DjangoFilterBackend

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


class ProjectList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def perform_create(self, serializer):
        serializer.save(author_user=self.request.user)


class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def patch(self, request, *args, **kwargs):
        res = {
            'detail': 'Méthode « PATCH » non autorisée.'}
        return Response(res, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ContributorList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Contributor.objects.all()
    serializer_class = ContributorSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['project_id']

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user.id)


class ContributorDelete(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Contributor.objects.all()
    serializer_class = ContributorSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['project_id', 'user_id']

    def perform_destroy(self, instance):
        if instance.user_id == self.request.user.id:
            instance.delete()


class IssueList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['project_id']

    def perform_create(self, serializer):
        serializer.save(author_user_id=self.request.user.id)


class IssueUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (AllowAny,)
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer

    def get(self, request, *args, **kwargs):
        res = {
            'detail': 'Méthode « GET » non autorisée.'}
        return Response(res, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        res = {
            'detail': 'Méthode « PATCH » non autorisée.'}
        return Response(res, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CommentList(generics.ListCreateAPIView):
    permission_classes = (AllowAny,)
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['project_id']

    def perform_create(self, serializer):
        serializer.save(author_user_id=self.request.user.id)


class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (AllowAny,)
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


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
