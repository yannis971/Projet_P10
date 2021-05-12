from rest_framework import serializers
from soft_desk.models import Comment
from soft_desk.models import Contributor
from soft_desk.models import Issue
from soft_desk.models import Project
from soft_desk.models import User



class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email', 'password']


class ProjectSerializer(serializers.ModelSerializer):
    author_user_id = serializers.ReadOnlyField(source='author_user.user_id')


    class Meta:
        model = Project
        fields = ['project_id', 'title', 'description', 'type', 'author_user_id']


class ContributorSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source='user.user_id')
    project_id = serializers.ReadOnlyField(source='project.project_id')

    class Meta:
        model = Contributor
        fields = ['user_id', 'project_id', 'permission', 'role']


class IssueSerializer(serializers.ModelSerializer):
    assignee_user_id = serializers.ReadOnlyField(source='assignee_user.user_id')
    author_user_id = serializers.ReadOnlyField(source='author_user.user_id')
    project_id = serializers.ReadOnlyField(source='project.project_id')


    class Meta:
        model = Issue
        fields = ['issue_id', 'title', 'desc', 'tag', 'priority', 'project_id', 'status', 'author_user_id', 'assignee_user_id', 'time_created']

    def validate(self, data):
        request = self._kwargs['context']['request']
        the_project = Project.objects.get(pk=request.parser_context['kwargs']['project_pk'])
        the_assignee_user = User.objects.get(pk=self._kwargs['data']['assignee_user_id'])
        if not the_assignee_user.is_contributor(the_project):
            raise serializers.ValidationError(f"assignee_user ({the_assignee_user.user_id} - {the_assignee_user}) is not a contributor to the project ({the_project.project_id} - {the_project})")
        return data


class CommentSerializer(serializers.ModelSerializer):
    issue_id = serializers.ReadOnlyField(source='issue.issue_id')
    author_user_id = serializers.ReadOnlyField(source='author_user.user_id')


    class Meta:
        model = Comment
        fields = ['comment_id', 'description', 'author_user_id', 'issue_id', 'time_created']
