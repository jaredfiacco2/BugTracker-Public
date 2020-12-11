from django.shortcuts import render,  get_object_or_404, redirect
from .models import Bug, BugWorkqueueStatus
from .forms import CreateBug, AdminUpdateBug, EmployeeUpdateBug
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max, F
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.db import connection
from pyclickup import ClickUp
from datetime import datetime

##Requestor Login: Request Fix
@login_required(login_url='/login/')
def bug_create_view(request):
    bug = CreateBug(request.POST or None)
    if bug.is_valid():
        newbug = bug.save(commit=False)    
        newbug.requestor   = request.user.first_name + ' ' + request.user.last_name
        newbug.requestor_email = request.user.email 
        newbug.save()

        #Add Clickup Task
        clickup = ClickUp("pk_10761609_CAP37AOETXJ3MVBXMQCI25CKW6LU5CO9")
        name = str(newbug.title)
        content = str(newbug.description) + '\n' + '\n' + 'Priority: ' + str(newbug.priority) + '\n' + 'Category: ' + str(newbug.category) + '\n' + 'Requestor Name: ' + str(newbug.requestor) + '\n' + 'Requestor Email:  ' + str(newbug.requestor_email)
        status = 'New Request'
        main_team = clickup.teams[0]
        main_space = main_team.spaces[0]
        main_project = main_space.projects[0]
        main_list = main_project.lists[0]

        #Back to Form
        bug = CreateBug()
        messages.success(request, 'Form successfully submitted.')
        try:
            main_list.create_task(name=name, content=content, status=status)
            messages.info(request, 'Clickup Task Generated - We will review and reach out to you shortly.')
        except:
            messages.error(request, 'Clickup Task Not Created - Please contact admin(s) to follow up.')
        return HttpResponseRedirect(reverse('home'))
        #return render(request, 'form/form_create_success.html')
    context = {
            'bug':bug,
        }
    return render(request, 'bug/bug_create.html', context)



##Employee/Admin: View All Submissions where 
@login_required(login_url='/login/')
def bug_list_view(request):
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
    #queryset = Bug.objects.all()
    queryset = Bug.objects.raw(""" select b.*, w.* from
                                                (select b.id, max(w.id) as max_s from bug_bug as b
                                                left join bug_bugworkqueuestatus as w on b.id=w.bug_wq_id
                                                group by b.id
                                                having max(bug_wq_id) is not null) as m_id
                                            left join bug_bug as b on b.id = m_id.id
                                            left join bug_bugworkqueuestatus as w on w.id = m_id.max_s """)
    context = {
        "filtered_bug_list" : filtered_queryset,
        "bug_list": queryset
    }
    return render(request, "bug/bug_list.html", context)

##Employee/Admin: View Specific Record, update record status
@login_required(login_url='/login/')
def bug_detail_view(request, id):
    bug = get_object_or_404(Bug, id=id)
    employeeform = EmployeeUpdateBug(request.POST or None)
    if employeeform.is_valid():
        update = employeeform.save(commit=False)
        update.bug_wq               = bug      
        update.workqueue_employee   = request.user             
        update.workqueue_lastupdatedts = timezone.now()
        update.save()
        messages.success(request, 'Changes successfully saved.')
        return HttpResponseRedirect(reverse('bug-wq'))
    context = {
        "employeeform" : employeeform,
        "bug_id": id,
        "bug" : bug
    }
    return render(request, "bug/bug_detail.html", context)

##ADMIN ONLY: Update Full Submission Detail
@login_required(login_url='/login/')
def bug_update_view(request, id=id):
    #if request.user.is_authenticated:
    bug = get_object_or_404(Bug, id=id)
    admin_form = AdminUpdateBug(request.POST or None, instance=bug)
    if admin_form.is_valid():
        admin_form.save()
        messages.success(request, 'Changes successfully saved.')
        return HttpResponseRedirect(reverse('bug-wq'))
    context = {
        'adminupdateform' : admin_form,
        'bug_id': id,
        'bug' : bug
    }
    return render(request, "bug/bug_update.html", context)
    #else:
    #    return render(request, 'app/login.html', locals())

##ADMIN ONLY: Delete Record
@login_required(login_url='/login/')
def bug_delete_view(request, id):
    bug = get_object_or_404(Bug, id=id)
    if request.method == "POST":
        obj.delete()
        messages.success(request, 'Record Successfully Deleted.')
        return HttpResponseRedirect(reverse('bug-wq'))
    context = {
        "bug": bug
    }
    return render(request, "bug/bug_delete.html", context)

##################################################################################################
##################################################################################################
################## Dashboard #####################################################################
##################################################################################################
##################################################################################################
##Requestor Login: Request Fix
@login_required(login_url='/login/')
def bug_dashboard(request):
    return render(request, 'bug/bug_dashboard.html')
    
#@login_required(login_url='/login/')
def data(request):

    #Request Dataset Query
    requests_queryset = Bug.objects.raw(""" select 1 as id, cast(cast(b.submission_dts as date) as text) as date, count(b.id) as count, '"' from
                                                bug_bug as b
                                                group by cast(b.submission_dts as date)
                                                order by cast(b.submission_dts as date) """)
    dataRows = []
    dataColumns = []
    response_data = {}

    #Make Request Data
    for r in requests_queryset:
        dataRows.append(r.date)
        dataRows.append(r.count)
        dataColumns.append(dataRows)
        dataRows = []
    response_data["values"] = dataColumns

    #Workqueue Dataset Query
    workqueue_queryset = Bug.objects.raw(""" select 1 as id, cast(cast(w.workqueue_lastupdatedts as date) as text) as date, count(w.id) as count, '"' from
                                                bug_bugworkqueueqtatus as w
                                                group by cast(w.submission_dts as date)
                                                order by cast(w.submission_dts as date) """)
    dataRows = []
    dataColumns = []
    response_data = {}

    #Workqueue Request Data
    for w in workqueue_queryset:
        dataRows.append(w.date)
        dataRows.append(w.count)
        dataColumns.append(dataRows)
        dataRows = []
    workqueue_data["values"] = dataColumns

    thedata = {
        "type": "line", 
        "title": {
            "text":"So cool its my graph finally"
        },
        "series": [response_data, workqueue_data]
    }
    return JsonResponse(thedata)

# @login_required(login_url='/login/')
# def zingchartConfig(request):
#     response_data = {}
#     response_data['title'].[0] = 'This Is My Calendar'
#     return JsonResponse(response_data)


####################################################################
##Test Dashboard JSON###############################################
def data_test(request):#########################################
    return render(request, "bug/bug_dashboard_test.html")###########
####################################################################
####################################################################

####################################################################
##Test Dashboard JSON###############################################
def data_test2(request):#########################################
    return render(request, "bug/bug_dashboard_test2.html")###########
####################################################################
####################################################################