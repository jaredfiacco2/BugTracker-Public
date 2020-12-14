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
        "x":0,
        "y":0,
        "width": "70%",
        "height": "25%",
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
            "lineColor": "#96feff",
            "lineWidth": "2px",
            "marker": {
                "backgroundColor": "#a3bcb8",
                "borderColor": "#88f5fa",
                "borderWidth": "2px",
                "shadow": "false"
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
        "x": "70%",
        "y": 0,
        "width": "30%",
        "height": "25%",
        "title": {
            "text":"Workqueue Updates Over Time",
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
        "plot": {
            "valueBox": {
            "visible": "false"
            },
            "animation": {
                "delay": 1300,
                "effect":   "ANIMATION_EXPAND_LEFT",
                "method":   "ANIMATION_LINEAR",
                "sequence": "ANIMATION_BY_PLOT",
                "speed":    "1800"
            },
            "lineColor": "#96feff",
            "lineWidth": "2px",
            "marker": {
                "backgroundColor": "#a3bcb8",
                "borderColor": "#88f5fa",
                "borderWidth": "2px",
                "shadow": "false"
            },
        },
        "plotarea": {
            "margin": "75px 75px 5px 67px"
        },
        "series": [workqueue_data]
    }
    return zingdata

################################################################################################################################################################
################################################### Pie Chart - Request Types ##################################################################################
################################################################################################################################################################
@login_required(login_url='/login/')
def zing_pie_requesttypes(request):

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
        "plot": {
            "valueBox": {
            "visible": "false"
            },
            "animation": {
                "delay": 1300,
                "effect":   "ANIMATION_EXPAND_LEFT",
                "method":   "ANIMATION_LINEAR",
                "sequence": "ANIMATION_BY_PLOT",
                "speed":    "1800"
            },
            "lineColor": "#96feff",
            "lineWidth": "2px",
            "marker": {
                "backgroundColor": "#a3bcb8",
                "borderColor": "#88f5fa",
                "borderWidth": "2px",
                "shadow": "false"
            },
        },
        "plotarea": {
            "margin": "75px 75px 5px 67px"
        },
        "series": [workqueue_data]
    }
    return zingdata

################################################################################################################################################################
################################################### Guage - Outstanding Request Count ##########################################################################
################################################################################################################################################################
@login_required(login_url='/login/')
def zing_guage_requestcount(request):

    #Workqueue Dataset Query
    workqueue_queryset = Bug.objects.raw("""  select 1 as id, count(*) count, '"'
                                                from
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
    dataColumns = []


    #Workqueue Request Data
    for w in workqueue_queryset:
        dataColumns.append(w.count)
    #workqueue_data["values"] = dataColumns
    title = "Count of Outstanding Requests"

    zingdata = {
        "type": "gauge",
        "globals": {
            "fontSize": "25px"
        },
        "backgroundColor": "#454754",
        "x": "33%",
        "y": "25%",
        "width": "33%",
        "height": "25%",
        "title": {
            "text": title,
            "paddingLeft": "20px",
            "backgroundColor": "none",
            "fontColor": "#ffffff",
            "fontFamily": "Arial",
            "fontSize": "18px",
            "fontWeight": "normal",
            "height": "40px",
            "textAlign": "left",
            "y": "10px"
        },
        "plot": {
            "valueBox": {
            "text": "%v",
            "fontSize": "25px",
            "placement": "center",
            "fontWeight": "normal",
            "rules": [
                {
                "text": "%v<br>Excellent",
                "rule": "%v <= 6"
                },
                {
                "text": "%v<br>Good",
                "rule": "%v > 6 && %v < 14"
                },
                {
                "text": "%v<br>Fair",
                "rule": "%v >= 14 && %v < 18"
                },
                {
                "text": "%v<br>Bad",
                "rule": "%v >= 18"
                }
            ]
            },
            "size": "100%"
        },
        "plotarea": {
            "marginTop": "80px"
        },
        "scaleR": {
            "aperture": 180,
            "center": {
                "visible": "false"
            },
            "item": {
            "offsetR": 0,
            "rules": [
                {
                "offsetX": "15px",
                "rule": "%i == 9"
                }
            ]
            },
            "labels": ["0", "4", "8", "12", "16", "20"],
            "maxValue": 20,
            "minValue": 0,
            "ring": {
            "rules": [
                {
                "backgroundColor": "#5FB83A",
                "rule": "%v <= 6"
                },
                {
                "backgroundColor": "#FFA726",
                "rule": "%v > 6 && %v < 14"
                },
                {
                "backgroundColor": "#EF5350",
                "rule": "%v >= 14 && %v < 18"
                },
                {
                "backgroundColor": "#E53935",
                "rule": "%v >= 18"
                }
            ],
            "size": "50px"
            },
            "step": 2,
            "tick": {
                "visible": "false"
            }
        },
        "tooltip": {
            "borderRadius": "5px"
        },
        "series": [
            {
            "values": dataColumns,
            "backgroundColor": "#ffffff",
            "indicator": [10, 10, 10, 10, 0.75],
            "animation": {
                "effect": "ANIMATION_EXPAND_VERTICAL",
                "method": "ANIMATION_BACK_EASE_OUT",
                "sequence": "null",
                "speed": 900
            }
            }
        ]
    }
    return zingdata


################################################################################################################################################################
################################################### Calendar - Workqueue #######################################################################################
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
        "backgroundColor": "#454754",
        "x": 0,
        "y": "75%",
        "width": "100%",
        "height": "25%",
        "title": {
            "text": title,
            "paddingLeft": '20px',
            "paddingTop": '15px',
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
            "marginTop": "25%",
            "marginBottom": "7%",
            "marginLeft": "10%",
            "marginRight": "5%",
        },
        "plot": {
            "animation": {
                "delay": 500,
                "effect": "ANIMATION_FADE_IN",
                "speed": "1800"
            },
            "tooltip": {
            "text": "%data-day:<br>%v statuses <br>updated.",
            "alpha": 0.8,
            "backgroundColor": "#454754",
            "borderColor": "#212121",
            "borderRadius": "3px",
            "fontColor": "white",
            "fontFamily": "Arial",
            "fontSize": "12px",
            "offsetY": "-10px",
            "textAlign": "center",
            "textAlpha": 1
            }
        },
        "options": {
                    "day": {
                        "inactive": {
                            "backgroundColor": "#F5F5F5",
                            "borderColor": "#ffffff"
                        },
                        "active": {
                            "backgroundColor": "#F5F5F5",
                            "borderColor": "#ffffff",
                            },
                    },
                    "month": {
                        "item": {
                            "fontColor": "white",
                            "fontFamily": "Arial",
                            "fontSize": "9px"
                        },
                        "outline": {
                            "active": {
                            "borderColor": "#454754"
                            },
                            "borderColor": "#454754"
                        }
                    },
                    "palette": ["#00ace6", "#b659b4"],
                    "rows": 2,
                    "scale": {
                        "width": "30%",
                        "height": "10px",
                        "x": "75%",
                        "paddingTop": '25px',
                    },
                    "weekday": {
                        "values": ["", "Mon", "", "Wed", "", "Fri", ""],
                        "item": {
                            "fontColor": "white",
                            "fontFamily": "Arial",
                            "fontSize": "9px"
                        }
                    },
                    "year": {
                        "text": year,
                        "visible": "true",
                        "fontColor": "white",
                        "fontFamily": "Arial",
                    },
                    "values": dataColumns
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
    for w in workqueue_queryset:
        dataRows.append(w.date)
        dataRows.append(w.count)
        dataColumns.append(dataRows)
        dataRows = []
        year = w.year
    title = 'Bug Requests Calendar - ' + year

    zingdata = {
        "type": "calendar",
        "backgroundColor": "#454754",
        "x": 0,
        "y": "50%",
        "width": "100%",
        "height": "25%",
        "title": {
            "text": title,
            "paddingLeft": '20px',
            "paddingTop": '15px',
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
            "marginTop": "25%",
            "marginBottom": "7%",
            "marginLeft": "10%",
            "marginRight": "5%",
        },
        "plot": {
            "animation": {
                "delay": 500,
                "effect": "ANIMATION_FADE_IN",
                "speed": "1800"
            },
            "tooltip": {
            "text": "%data-day:<br>%v statuses <br>updated.",
            "alpha": 0.8,
            "backgroundColor": "#454754",
            "borderColor": "#212121",
            "borderRadius": "3px",
            "fontColor": "white",
            "fontFamily": "Arial",
            "fontSize": "12px",
            "offsetY": "-10px",
            "textAlign": "center",
            "textAlpha": 1
            }
        },
        "options": {
                    "day": {
                        "inactive": {
                            "backgroundColor": "#F5F5F5",
                            "borderColor": "#ffffff"
                        },
                        "active": {
                            "backgroundColor": "#F5F5F5",
                            "borderColor": "#ffffff",
                            },
                    },
                    "month": {
                        "item": {
                            "fontColor": "white",
                            "fontFamily": "Arial",
                            "fontSize": "9px"
                        },
                        "outline": {
                            "active": {
                            "borderColor": "#454754"
                            },
                            "borderColor": "#454754"
                        }
                    },
                    "palette": ["#00ace6", "#b659b4"],
                    "rows": 2,
                    "scale": {
                        "width": "30%",
                        "height": "10px",
                        "x": "75%",
                        "paddingTop": '25px',
                    },
                    "weekday": {
                        "values": ["", "Mon", "", "Wed", "", "Fri", ""],
                        "item": {
                            "fontColor": "white",
                            "fontFamily": "Arial",
                            "fontSize": "9px"
                        }
                    },
                    "year": {
                        "text": year,
                        "visible": "true",
                        "fontColor": "white",
                        "fontFamily": "Arial",
                    },
                    "values": dataColumns
                },
        }

    return zingdata

################################################################################################################################################################
################################################### Dashboard - Putting It All Together ########################################################################
################################################################################################################################################################
@login_required(login_url='/login/')
def zing_dashboard(request):

    line_requests       = zing_line_request(request)
    line_workqueue      = zing_line_wqupdates(request) 
    cal_workqueue       = zing_cal_wqupdates(request)
    cal_requests        = zing_cal_requests(request)
    guage_requestcount  = zing_guage_requestcount(request)

    zingdata =  {
                "backgroundColor": "#454754",
                "layout": "2x2",
                "graphset":   [
                                line_requests, line_workqueue, guage_requestcount, cal_requests, cal_workqueue
                            ]
                }

    return JsonResponse(zingdata)