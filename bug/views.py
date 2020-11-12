from django.shortcuts import render,  get_object_or_404, redirect
from .models import Bug
from .forms import CreateBug, AdminUpdateBug, EmployeeUpdateBug
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max, F
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils import timezone
from django.db import connection

##Patient Submission
def bug_create_view(request):
    bug = CreateBug(request.POST or None)
    if bug.is_valid():
        bug.save()
        bug = CreateBug()
        messages.success(request, 'Form successfully submitted. We will reach out to you soon.')
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
        return HttpResponseRedirect(reverse('bug-list'))
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
        return HttpResponseRedirect(reverse('bug-list'))
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
        return HttpResponseRedirect(reverse('bug-list'))
    context = {
        "bug": bug
    }
    return render(request, "bug/bug_delete.html", context)
