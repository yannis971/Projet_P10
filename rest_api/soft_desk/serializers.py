from rest_framework import serializers
from soft_desk.models import User

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    user_id = serializers.ReadOnlyField(source='user.id')
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'type', 'user_id']
