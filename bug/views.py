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
import requests

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

################################################################################################################################################################    
################################################################################################################################################################
################################################################################################################################################################
######################################################## Dashboard Section #####################################################################################
################################################################################################################################################################
################################################################################################################################################################
################################################################################################################################################################

################################################################################################################################################################
############################################## Double Line Chart - Requests Over Time ##########################################################################
################################################################################################################################################################
@login_required(login_url='/login/')
def zing_line_request(request):

    #Request Dataset Query
    requests_queryset = Bug.objects.raw(""" 
                                            select 
                                                1 as id, 
                                                cast(cast(b.submission_dts as date) as text) as date, 
                                                count(b.id) as count, 
                                                '"' 
                                            from
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

    zingdata = {
        "type": "line", 
        "backgroundColor": "#454754",
        "width": "70%",
        "title": {
            "text":"Requests Over Time",
            "paddingLeft": '20px',
            "backgroundColor": 'none',
            "fontColor": '#ffffff',
            "fontFamily": 'Arial',
            "fontSize": '18px',
            "fontWeight": 'normal',
            "height": '40px',
            "textAlign": 'left',
            "y": '10px'
        },
        "plotarea": {
        "margin": "75px 75px 5px 67px"
        },
        "plot": {
            "valueBox": {
            "visible": "false"
            },
            "animation": {
                "delay": 500,
                "effect":   "ANIMATION_EXPAND_LEFT",
                "method":   "ANIMATION_LINEAR",
                "sequence": "ANIMATION_BY_PLOT",
                "speed":    "1800"
            },
        },
        "tooltip": {
            "padding": "5px 10px",
            "backgroundColor": "#54ced4",
            "borderRadius": "6px",
            "fontColor": "#454754",
            "shadow": "false"
        },
        "lineColor": "#96feff",
        "lineWidth": "2px",
        "marker": {
            "backgroundColor": "#a3bcb8",
            "borderColor": "#88f5fa",
            "borderWidth": "2px",
            "shadow": "false"
        },
        "series": [response_data],
    }
    return zingdata

################################################################################################################################################################
################################################### Line Chart - Workqueue Updates #############################################################################
################################################################################################################################################################
@login_required(login_url='/login/')
def zing_line_wqupdates(request):

    #Workqueue Dataset Query
    workqueue_queryset = Bug.objects.raw(""" select 1 as id, cast(cast(w.workqueue_lastupdatedts as date) as text) as date, count(w.id) as count, '"' from
                                                bug_bugworkqueuestatus as w
                                                group by cast(w.workqueue_lastupdatedts as date)
                                                order by cast(w.workqueue_lastupdatedts as date) """)
    dataRows = []
    dataColumns = []
    workqueue_data = {}

    #Workqueue Request Data
    for w in workqueue_queryset:
        dataRows.append(w.date)
        dataRows.append(w.count)
        dataColumns.append(dataRows)
        dataRows = []
    workqueue_data["values"] = dataColumns

    zingdata = {
        "type": "line", 
        "backgroundColor": "#454754",
        "width": "34%",
        "x": "66%",
        "title": {
            "text":"Workqueue Updates Over Time",
            "backgroundColor": "none",
            "fontColor": "#ffffff",
            "fontFamily": "Arial",
            "fontWeight": "normal",
            "height": "40px"
        },
        "plot": {
            "valueBox": {
            "visible": "false"
            },
            "animation": {
                "delay": 2300,
                "effect":   "ANIMATION_EXPAND_LEFT",
                "method":   "ANIMATION_LINEAR",
                "sequence": "ANIMATION_BY_PLOT",
                "speed":    "1800"
            },
        },
        "plotarea": {
            "margin": "60px 10px 0px 0px"
        },
        "series": [workqueue_data]
    }
    return zingdata

################################################################################################################################################################
################################################### Calendar - Workqueue #############################################################################
################################################################################################################################################################
@login_required(login_url='/login/')
def zing_cal_wqupdates(request):

    #Workqueue Dataset Query
    workqueue_queryset = Bug.objects.raw(""" 
                                            select 
                                                    1 as id, cast(cast(w.workqueue_lastupdatedts as date) as text) as date, 
                                                    count(w.id) as count, 
                                                    cast(to_char(cast(w.workqueue_lastupdatedts as date), 'YYYY') as text) as year, 
                                                    '"' 
                                            from
                                                bug_bugworkqueuestatus as w
                                                group by cast(w.workqueue_lastupdatedts as date)
                                                order by cast(w.workqueue_lastupdatedts as date) """)
    dataRows = []
    dataColumns = []
    ##workqueue_data = {}

    #Workqueue Request Data
    for w in workqueue_queryset:
        dataRows.append(w.date)
        dataRows.append(w.count)
        dataColumns.append(dataRows)
        dataRows = []
        year = w.year
    title = 'Workqueue Status Update Calendar - ' + year

    zingdata = {
        "type": "calendar",
        "options": {
                    "year": {
                    "text": year,
                    "visible": "false"
                    },
                    "startMonth": 1,
                    "endMonth": 12,
                    "palette": ["none", "#2196F3"],
                    "month": {
                    "item": {
                        "fontColor": "gray",
                        "fontSize": 9
                    }
                    },
                    "weekday": {
                    "values": ["","M","","W","","F",""],
                    "item":{
                        "fontColor": "gray",
                        "fontSize":9
                    }
                    },
                    "values": dataColumns
                },
        "labels": [
            { ##Title
            "text": title,
            "textAlign": 'center',
            "x": "10%",
            "y":"2.5%",
            "width": "80%",
            "height": "5%",
            "fontFamily": "Georgia",
            "fontColor": "#1c4966",
            "fontSize": 35,
            },
            { ##Lefthand Label (container portion)
            "borderColor": "gray",
            "borderWidth": 1,
            "x": "8%",
            "y": "60%",
            "width": "40%",
            "height": "30%"
            },
            { ##Lefthand Label (top portion)
            "text": "Daily Contribution",
            "fontColor": "#212121",
            "textAlign": "center",
            "x": "10%",
            "y":"65%",
            "width": "36%"
            },
            { ##Lefthand Label (middle portion)
            "text": "%plot-value",
            "fontColor": "#2196F3",
            "fontFamily": "Georgia",
            "fontSize": 35,
            "textAlign": "center",
            "x": "10%",
            "y": "68%",
            "width": "36%"
            },
            ## Note: the bottom portion of the Bottom-Left Label is the fixed tooltip, below.
            
            { ##Rightside Label (container portion)
            "borderColor": "gray",
            "borderWidth": 1,
            "x": "52%",
            "y": "60%",
            "width": "40%",
            "height": "30%",
            },
            { ##Rightside Label (top portion)
            "text": "Total Contributions",
            "fontColor": "#212121",
            "textAlign": "center",
            "x": "54%",
            "y": "65%",
            "width": "36%"
            },
            { ##Rightside Label (middle portion)
            "text": "1414",
            "fontColor": "#2196F3",
            "fontFamily": "Georgia",
            "fontSize": 35,
            "textAlign": "center",
            "x": "54%",
            "y": "68%",
            "width": "36%"
            },
            { ##Rightside Label (bottom portion)
            "text": "Jan 1 - Jun 30",
            "fontColor": "#212121",
            "padding": 2,
            "textAlign": "center",
            "x": "54%",
            "y": "80%",
            "width": "36%"
            }
        ],
        
        "tooltip" : { ##Lefthand Label (bottom portion)
            "text": "%data-day",
            "backgroundColor": "none",
            "borderColor": "none",
            "fontColor": "#212121",
            "padding": 2,
            ##textAlign: "center",
            "align": "center",
            "sticky": "true",
            "timeout": 30000,
            "x": "10%",
            "y": "80%",
            "width": "36%"
        },
        

        }

    return zingdata

################################################################################################################################################################
################################################### Calendar - Request Data ####################################################################################
################################################################################################################################################################
@login_required(login_url='/login/')
def zing_cal_requests(request):

    #Workqueue Dataset Query
    workqueue_queryset = Bug.objects.raw(""" 
                                            select 
                                                1 as id, 
                                                cast(cast(b.submission_dts as date) as text) as date, 
                                                count(b.id) as count, 
                                                cast(to_char(cast(b.submission_dts as date), 'YYYY') as text) as year,
                                                '"' 
                                            from
                                                bug_bug as b
                                                group by cast(b.submission_dts as date)
                                                order by cast(b.submission_dts as date) """)
    dataRows = []
    dataColumns = []
    ##workqueue_data = {}

    #Workqueue Request Data
    for r in workqueue_queryset:
        dataRows.append(r.date)
        dataRows.append(r.count)
        dataColumns.append(dataRows)
        dataRows = []
        year = r.year
    title = 'New Bug Submissions Calendar - ' + year

    zingdata = {
        "type": "calendar",
        "plotarea":   {
                    "margin": "45px 30px 40px 65px"
                    },
        "backgroundColor": "#454754",
        "borderBottom": "8px solid #565867",
        "width": "100%",
        "plot": {
            "animation": {
                "delay": 0,
                "effect": "ANIMATION_EXPAND_BOTTOM",
                "method": "ANIMATION_LINEAR",
                "sequence": "ANIMATION_NO_SEQUENCE",
                "speed": "1000"
            },
        },
        "options": {
                    "year": {
                    "text": year,
                    "visible": "false"
                    },
                    "startMonth": 1,
                    "endMonth": 12,
                    "palette": ["none", "#2196F3"],
                    "month": {
                    "item": {
                        "fontColor": "gray",
                        "fontSize": 9
                    }
                    },
                    "weekday": {
                    "values": ["","M","","W","","F",""],
                    "item":{
                        "fontColor": "gray",
                        "fontSize":9
                    }
                    },
                    "values": dataColumns
                },
        "labels": [
            { ##Title
            "text": title,
            "textAlign": 'center',
            "x": "10%",
            "width": "80%",
            "paddingLeft": '20px',
            "backgroundColor": 'none',
            "fontColor": '#ffffff',
            "fontFamily": 'Arial',
            "fontSize": '18px',
            "fontWeight": 'normal',
            "height": '40px',
            "textAlign": 'left',
            "y": '10px'
            },
            { ##Lefthand Label (container portion)
            "borderColor": "gray",
            "borderWidth": 1,
            "x": "8%",
            "y": "60%",
            "width": "40%",
            "height": "30%"
            },
            { ##Lefthand Label (top portion)
            "text": "Daily Contribution",
            "fontColor": "#212121",
            "textAlign": "center",
            "x": "10%",
            "y":"65%",
            "width": "36%"
            },
            { ##Lefthand Label (middle portion)
            "text": "%plot-value",
            "fontColor": "#2196F3",
            "fontFamily": "Georgia",
            "fontSize": 35,
            "textAlign": "center",
            "x": "10%",
            "y": "68%",
            "width": "36%"
            },
            ## Note: the bottom portion of the Bottom-Left Label is the fixed tooltip, below.
            
            { ##Rightside Label (container portion)
            "borderColor": "gray",
            "borderWidth": 1,
            "x": "52%",
            "y": "60%",
            "width": "40%",
            "height": "30%",
            },
            { ##Rightside Label (top portion)
            "text": "Total Contributions",
            "fontColor": "#212121",
            "textAlign": "center",
            "x": "54%",
            "y": "65%",
            "width": "36%"
            },
            { ##Rightside Label (middle portion)
            "text": "1414",
            "fontColor": "#2196F3",
            "fontFamily": "Georgia",
            "fontSize": 35,
            "textAlign": "center",
            "x": "54%",
            "y": "68%",
            "width": "36%"
            },
            { ##Rightside Label (bottom portion)
            "text": "Jan 1 - Jun 30",
            "fontColor": "#212121",
            "padding": 2,
            "textAlign": "center",
            "x": "54%",
            "y": "80%",
            "width": "36%"
            }
        ],
        
        "tooltip" : { ##Lefthand Label (bottom portion)
            "text": "%data-day",
            "backgroundColor": "none",
            "borderColor": "none",
            "fontColor": "#212121",
            "padding": 2,
            ##textAlign: "center",
            "align": "center",
            "sticky": "true",
            "timeout": 30000,
            "x": "10%",
            "y": "80%",
            "width": "36%"
        },
        

        }

    return zingdata

################################################################################################################################################################
################################################### Dashboard - Putting It All Together ########################################################################
################################################################################################################################################################
@login_required(login_url='/login/')
def zing_dashboard(request):

    line_requests   =   zing_line_request(request)
    line_workqueue  =   zing_line_wqupdates(request) 
    cal_workqueue   =   zing_cal_wqupdates(request)

    zingdata =  {
                "backgroundColor": "#454754",
                "graphset":   [
                                line_requests, line_workqueue, cal_workqueue, 
                            ]
                }

    return JsonResponse(zingdata)