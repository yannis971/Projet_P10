from rest_framework import serializers
from soft_desk.models import Comment
from soft_desk.models import Contributor
from soft_desk.models import Issue
from soft_desk.models import Project
from soft_desk.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    User serializer
    """
    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email', 'password']

    def validate(self, data):
        try:
            first_name = self._kwargs['data']['first_name']
        except KeyError:
            first_name = ""
        try:
            last_name = self._kwargs['data']['last_name']
        except KeyError:
            last_name = ""
        if not (first_name and last_name):
            message = "you must set a not empty string value for first_name and last_name"
            raise serializers.ValidationError(message)
        return data


class ProjectSerializer(serializers.ModelSerializer):
    """
    Project serializer
    """
    author_user_id = serializers.ReadOnlyField(source='author_user.user_id')

    class Meta:
        model = Project
        fields = ['project_id', 'title', 'description', 'type', 'author_user_id']


class ContributorSerializer(serializers.ModelSerializer):
    """
    Contributor serializer
    """
    user_id = serializers.ReadOnlyField(source='user.user_id')
    project_id = serializers.ReadOnlyField(source='project.project_id')

    class Meta:
        model = Contributor
        fields = ['user_id', 'project_id', 'permission', 'role']


class IssueSerializer(serializers.ModelSerializer):
    """
    Issue serializer
    """
    assignee_user_id = serializers.ReadOnlyField(source='assignee_user.user_id')
    author_user_id = serializers.ReadOnlyField(source='author_user.user_id')
    project_id = serializers.ReadOnlyField(source='project.project_id')

    class Meta:
        model = Issue
        fields = ['issue_id', 'title', 'desc', 'tag', 'priority',
                  'project_id', 'status', 'author_user_id',
                  'assignee_user_id', 'time_created']

    def validate(self, data):
        request = self._kwargs['context']['request']
        the_project = Project.objects.get(pk=request.parser_context['kwargs']['project_pk'])
        the_assignee_user = User.objects.get(pk=self._kwargs['data']['assignee_user_id'])
        if not the_assignee_user.is_contributor(the_project) \
                and not (the_assignee_user == the_project.author_user):
            raise serializers.ValidationError(f"assignee_user ({the_assignee_user.user_id}) \
                 has no permission (contributor or owner) in project ({the_project.project_id})")
        return data


class CommentSerializer(serializers.ModelSerializer):
    """
    Comment serializer
    """
    issue_id = serializers.ReadOnlyField(source='issue.issue_id')
    author_user_id = serializers.ReadOnlyField(source='author_user.user_id')

    class Meta:
        model = Comment
        fields = ['comment_id', 'description', 'author_user_id', 'issue_id', 'time_created']
