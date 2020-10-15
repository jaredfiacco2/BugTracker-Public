from django.shortcuts import render,  get_object_or_404, redirect
from .models import Bug
from .forms import CreateBug, AdminUpdateBug, EmployeeUpdateBug
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max, F
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils import timezone

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
#    filtered_queryset = Bug.objects.exclude( Q(workqueue_status = 'Voicemail 3X - Could Not Reach') | Q(workqueue_status = 'Declided') | Q(workqueue_status = 'Declined') | Q(workqueue_status = 'Duplicate') | Q(workqueue_status = 'Scheduled')) # list of objects 
    filtered_queryset = Bug.objects.annotate(max_wqid=Max('statuses')).filter(statuses=F('max_wqid')).select_related()
    queryset = Bug.objects.all()
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
