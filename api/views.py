from django.apps import apps
Bug = apps.get_model('bug', 'Bug')
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max, F
from django.db import connection
from django.core import serializers
from django.http import HttpResponse


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

