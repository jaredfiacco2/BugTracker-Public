from django.contrib.auth.models import User, Group
from rest_framework import serializers
##from django.apps import apps
##Bug = apps.get_model('bug', 'Bug')
from django.apps.get_model import Bug

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

class BugSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Bug
        fields = ['title', 'description', 'priority', 'category', 'submission_dts', 'requestor', 'requestor_email']