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


class CommentSerializer(serializers.ModelSerializer):
    issue_id = serializers.ReadOnlyField(source='issue.issue_id')
    author_user_id = serializers.ReadOnlyField(source='author_user.user_id')


    class Meta:
        model = Comment
        fields = ['comment_id', 'description', 'author_user_id', 'issue_id', 'time_created']
