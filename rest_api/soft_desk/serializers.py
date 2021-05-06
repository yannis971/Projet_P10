from rest_framework import serializers
from soft_desk.models import Comment
from soft_desk.models import Contributor
from soft_desk.models import Issue
from soft_desk.models import Project
from soft_desk.models import User


class UserSerializer(serializers.HyperlinkedModelSerializer):


    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email', 'password']


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    author_user = serializers.ReadOnlyField(source='author_user.username')
    author_user_id = serializers.ReadOnlyField(source='author_user.user_id')


    class Meta:
        model = Project
        fields = ['project_id', 'title', 'description', 'type', 'author_user_id']


class ContributorSerializer(serializers.HyperlinkedModelSerializer):
    user_id = serializers.ReadOnlyField(source='user.user_id')
    project_id = serializers.ReadOnlyField(source='project.project_id')


    class Meta:
        model = Contributor
        fields = ['user_id', 'project_id', 'permission', 'role']


class IssueSerializer(serializers.HyperlinkedModelSerializer):
    author_user_id = serializers.ReadOnlyField(source='author_user.user_id')
    project_id = serializers.ReadOnlyField(source='project.project_id')
    assignee_user_id = serializers.ReadOnlyField(source='assignee_user.user_id')


    class Meta:
        model = Issue
        fields = ['title', 'desc', 'tag', 'priority', 'project_id', 'status', 'author_user_id', 'assignee_user_id', 'time_created']


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    issue_id = serializers.ReadOnlyField(source='issue.id')
    author_user_id = serializers.ReadOnlyField(source='author_user.user_id')


    class Meta:
        model = Comment
        fields = ['comment_id', 'description', 'author_user_id', 'issue_id', 'time_created']
