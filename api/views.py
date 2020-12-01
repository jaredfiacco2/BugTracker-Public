# from django.apps import apps
# Bug = apps.get_model('bug', 'Bug')
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max, F
from django.db import connection
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
# from .serializers import BugSerializer
from bug.models import Bug, BugWorkqueueStatus


from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from .serializers import UserSerializer, GroupSerializer, BugSerializer, BugsSerializer


##################################### API/JSON Views #############################
##Employee/Admin: View All Submissions where
@login_required(login_url='/login/')
def json_bug_list_all(request):
    #queryset = Bug.objects.all()
    queryset = Bug.objects.raw(""" select b.*, w.* from
                                                (select b.id, max(w.id) as max_s from bug_bug as b
                                                left join bug_bugworkqueuestatus as w on b.id=w.bug_wq_id
                                                group by b.id
                                                having max(bug_wq_id) is not null) as m_id
                                            left join bug_bug as b on b.id = m_id.id
                                            left join bug_bugworkqueuestatus as w on w.id = m_id.max_s """)

    qs_json = serializers.serialize('json', queryset)
    return HttpResponse(qs_json, content_type='application/json')
@login_required(login_url='/login/')
def json_bug_list_wq(request):
    filtered_queryset = Bug.objects.raw(""" select b.*, w.* from
                                                (select b.id, max(w.id) as max_s from bug_bug as b
                                                left join bug_bugworkqueuestatus as w on b.id=w.bug_wq_id
                                                group by b.id
                                                having max(bug_wq_id) is not null) as m_id
                                            left join bug_bug as b on b.id = m_id.id
                                            left join bug_bugworkqueuestatus as w on w.id = m_id.max_s
                                            where
                                                w.workqueue_status <> 'Duplicate' and
                                                w.workqueue_status Not Like '%%t Fix (%%' and
                                                w.workqueue_status Not Like '%%Fixe%%' and
                                                w.workqueue_status <> 'Closed' """)
    qs_json = serializers.serialize('json', filtered_queryset)
    return HttpResponse(qs_json, content_type='application/json')


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

class BugsSerializer(viewsets.ModelViewSet):
    bugs = Bug.objects.all()
    serializer_class = BugsSerializer
    permission_classes = [permissions.IsAuthenticated]


bugs = Bug.objects.all()
@login_required(login_url='/login/')
@api_view(['GET'])
def restApiBugList(request):
    
    serializer_class = BugSerializer(bugs, many=True)
    return Response(serializer_class.data)

