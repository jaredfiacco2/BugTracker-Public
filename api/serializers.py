from django.contrib.auth.models import User, Group
from rest_framework import serializers
from bug.models import Bug, BugWorkqueueStatus

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

class BugListAllSerializer(serializers.HyperlinkedModelSerializer):
    workqueue_status                = serializers.CharField()
    workqueue_comment               = serializers.CharField()
    submission_id                   = serializers.CharField()
    submission_hyperlink            = serializers.CharField()
    class Meta:
        model = Bug
        fields = ['url', 'title', 'description', 'priority', 'category', 'submission_dts', 'requestor', 'requestor_email', 'workqueue_status', 'workqueue_comment', 'submission_id', 'submission_hyperlink']

class BugListFilteredSerializer(serializers.HyperlinkedModelSerializer):
    workqueue_status                = serializers.CharField()
    workqueue_comment               = serializers.CharField()
    submission_id                   = serializers.CharField()
    submission_hyperlink            = serializers.CharField()
    class Meta:
        model = Bug
        fields = ['url', 'title', 'description', 'priority', 'category', 'submission_dts', 'requestor', 'requestor_email', 'workqueue_status', 'workqueue_comment', 'submission_id', 'submission_hyperlink']