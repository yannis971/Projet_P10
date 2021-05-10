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
    user_id = serializers.IntegerField(source='user.user_id')
    project_id = serializers.IntegerField(source='project.project_id')


    class Meta:
        model = Contributor
        fields = ['user_id', 'project_id', 'permission', 'role']

    def create(self, validated_data):
        the_user = User.objects.get(pk=validated_data['user']['user_id'])
        validated_data.pop('user')
        the_project = Project.objects.get(pk=validated_data['project']['project_id'])
        validated_data.pop('project')
        instance = Contributor.objects.create(user=the_user, project=the_project, **validated_data)
        return instance


class IssueSerializer(serializers.ModelSerializer):
    assignee_user_id = serializers.IntegerField(source='assignee_user.user_id')
    author_user_id = serializers.IntegerField(source='author_user.user_id')
    project_id = serializers.IntegerField(source='project.project_id')


    class Meta:
        model = Issue
        fields = ['issue_id', 'title', 'desc', 'tag', 'priority', 'project_id', 'status', 'author_user_id', 'assignee_user_id', 'time_created']

    def create(self, validated_data):
        the_assignee_user = User.objects.get(pk=validated_data['assignee_user']['user_id'])
        validated_data.pop('assignee_user')
        the_author_user = User.objects.get(pk=validated_data['author_user']['user_id'])
        validated_data.pop('author_user')
        the_project = Project.objects.get(pk=validated_data['project']['project_id'])
        validated_data.pop('project')
        instance = Issue.objects.create(assignee_user=the_assignee_user, author_user=the_author_user, project=the_project, **validated_data)
        return instance

    def update(self, instance, validated_data):
        instance.assignee_user_id = validated_data['assignee_user']['user_id']
        validated_data.pop('assignee_user')
        instance.author_user_author = validated_data['author_user']['user_id']
        validated_data.pop('author_user')
        instance.project_id = validated_data['project']['project_id']
        validated_data.pop('project')
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class CommentSerializer(serializers.ModelSerializer):
    issue_id = serializers.IntegerField(source='issue.id')
    author_user_id = serializers.IntegerField(source='author_user.user_id')


    class Meta:
        model = Comment
        fields = ['comment_id', 'description', 'author_user_id', 'issue_id', 'time_created']

    def create(self, validated_data):
        the_author_user = User.objects.get(pk=validated_data['author_user']['user_id'])
        validated_data.pop('author_user')
        the_issue = Issue.objects.get(pk=validated_data['issue']['issue_id'])
        validated_data.pop('issue')
        instance = Comment.objects.create(author_user=the_author_user, issue=the_issue, **validated_data)
        return instance
