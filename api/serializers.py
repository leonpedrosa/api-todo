from django.contrib.auth.models import User
from rest_framework import serializers
from api.models import Task


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password')


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'finished', 'user_id')
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = self.context['request'].user
        task = Task.objects.create(user=user, **validated_data)
        return task
