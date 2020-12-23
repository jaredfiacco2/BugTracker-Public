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
############################################## Pareto Chart - Requests By User #################################################################################
################################################################################################################################################################
@login_required(login_url='/login/')
def zing_pareto_request(request):

    #Request Dataset Query
    requests_queryset = Bug.objects.raw(""" 
                                            select 
                                                1 as id, 
                                                b.requestor as user, 
                                                count(b.id) as count, 
                                                '"' 
                                            from
                                                bug_bug as b
                                                group by b.requestor 
                                                order by count(b.id) desc """)
    dataUsers = []
    dataCount = []

    #Make Request Data
    for r in requests_queryset:
        dataUsers.append(r.user)
        dataCount.append(r.count)

    zingdata = {
        "type": "pareto", 
        "backgroundColor": "#454754",
        "x":0,
        "y":0,
        "width": "70%",
        "height": "22%",
        "title": {
            "text":"Requests By User",
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
        "scaleX": {
            "labels": dataUsers
        },
        "scaleY": {
            "guide": {
                "lineStyle": "solid"
            },
            "label": {
                "text": "Requests Per User",
                "fontColor": "#ffffff",
                "fontFamily": "Arial",
                "fontSize": "11px",
                "fontWeight": "normal"
            },
        },
        "scaleY2": {
            "guide": {
                "lineStyle": "solid"
            },
            "label": {
                "text": "Cumulative Percentage",
                "fontColor": "#ffffff",
                "fontFamily": "Arial",
                "fontSize": "11px",
                "fontWeight": "normal",
                "offsetX": "5px"
            },
        },
        "series": [
            {
                "values": dataCount,
                "backgroundColor": "#0097A7",
                "barWidth": '90%'
            }
        ]
    }
    return zingdata

####################################################################################################################################################
######################################################### Horiontal Bar Chart - Workqueue Updates Hour Distribution ################################
####################################################################################################################################################
@login_required(login_url='/login/')
def zing_hbar_wqupdates(request):

    #Workqueue Dataset Query
    workqueue_queryset = Bug.objects.raw(""" 
                                            select 
                                                1 as id
                                                ,count(*) count
                                                ,extract(hour from workqueue_lastupdatedts at time zone 'utc' at time zone 'est') as hour
                                                ,'"'
                                            from bug_bugworkqueuestatus

                                            group by extract(hour from workqueue_lastupdatedts at time zone 'utc' at time zone 'est')
                                            order by extract(hour from workqueue_lastupdatedts at time zone 'utc' at time zone 'est') 
                                        """)
    
    twelveAm, oneAm, twoAm, threeAm, fourAm, fiveAm, sixAm, sevenAm, eightAm, nineAm, tenAm, elevenAm  = 0,0,0,0,0,0,0,0,0,0,0,0
    twelvePm, onePm, twoPm, threePm, fourPm, fivePm, sixPm, sevenPm, eightPm, ninePm, tenPm, elevenPm = 0,0,0,0,0,0,0,0,0,0,0,0

    #Workqueue Request Data
    for w in workqueue_queryset:
        if   w.hour == 0:
            twelveAm = w.count
        elif w.hour == 1:
            oneAm = w.count
        elif w.hour == 2:
            twoAm = w.count
        elif w.hour == 3:
            threeAm = w.count
        elif w.hour == 4:
            fourAm = w.count
        elif w.hour == 5:
            fiveAm = w.count
        elif w.hour == 6:
            sixAm = w.count
        elif w.hour == 7:
            sevenAm = w.count
        elif w.hour == 8:
            eightAm = w.count
        elif w.hour == 9:
            nineAm = w.count
        elif w.hour == 10:
            tenAm = w.count
        elif w.hour == 11:
            elevenAm = w.count
        elif w.hour == 12:
            twelvePm = w.count
        elif w.hour == 13:
            onePm = w.count
        elif w.hour == 14:
            twoPm = w.count
        elif w.hour == 15:
            threePm = w.count
        elif w.hour == 16:
            fourPm = w.counto
        elif w.hour == 17:
            fivePm = w.count
        elif w.hour == 18:
            sixPm = w.count
        elif w.hour == 19:
            sevenPm = w.count
        elif w.hour == 20:
            eightPm = w.count
        elif w.hour == 21:
            ninePm = w.count
        elif w.hour == 22:
            tenPm = w.count
        elif w.hour == 23:
            elevenPm = w.count
    dataRows = [twelveAm, oneAm, twoAm, threeAm, fourAm, fiveAm, sixAm, sevenAm, eightAm, nineAm, tenAm, elevenAm, twelvePm, onePm, twoPm, threePm, fourPm, fivePm, sixPm, sevenPm, eightPm, ninePm, tenPm, elevenPm]

    zingdata = {
        "type": "hbar", 
        "backgroundColor": "#454754",
        "x": "70%",
        "y": 0,
        "width": "30%",
        "height": "22%",
        "title": {
            "text":"Workqueue Updates - Hourly Dist",
            "paddingLeft": '20px',
            "backgroundColor": 'none',
            "fontColor": '#ffffff',
            "fontFamily": 'Arial',
            "fontSize": '18px',
            "fontWeight": 'normal',
            "height": '40px',
            "textAlign": 'center',
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
            "barColor": "#96feff",
            "barWidth": "70%",

        },
        "plotarea": {
            "margin": "75px 75px 5px 67px"
        },
        "scaleX": {
            "label": {
                "text": "Hour",
                "fontColor": "#ffffff",
                "fontFamily": "Arial",
                "fontSize": "11px",
                "fontWeight": "normal"
            }

        },
        "scaleY": {
            "label": {
                "text": "Requests Per Hour",
                "fontColor": "#ffffff",
                "fontFamily": "Arial",
                "fontSize": "11px",
                "fontWeight": "normal"
            },
        },
        "series": [{
            "values": dataRows,
            "backgroundColor": "#0097A7",
        }]
    }
    return zingdata

################################################################################################################################################################
################################################### Pie Chart - Request Category ###############################################################################
################################################################################################################################################################
@login_required(login_url='/login/')
def zing_pie_requestcatagory(request):

    #Workqueue Dataset Query
    workqueue_queryset = Bug.objects.raw("""    select 
                                                    1 as id,  
                                                    count(*) count, 
                                                    b.category, '"'
                                                from bug_bug as b
                                                group by b.category """)
    buggie = 0
    featreq = 0
    custiss = 0
    intcl = 0
    proc = 0
    vuln = 0
    title = "Category Types Pie Chart"

    #Workqueue Request Data
    for w in workqueue_queryset:
        if w.category == "Bug":
            buggie = w.count
        elif w.category == "Feature Request":
            featreq = w.count
        elif w.category =="Customer Issue":
            custiss = w.count
        elif w.category =="Internal Cleanup":
            intcl = w.count
        elif w.category =="Process":
            proc = w.count
        elif w.category =="Vulnerability":
            vuln = w.count
        

    zingdata = {
        "type":"pie",
        "backgroundColor": "#454754",
        "x": "1%",
        "y": "25%",
        "width": "30%",
        "height": "25%",
        "title": {
            "text":title,
            "paddingLeft": '20px',
            "backgroundColor": 'none',
            "fontColor": '#ffffff',
            "fontFamily": 'Arial',
            "fontSize": '18px',
            "fontWeight": 'normal',
            "height": '40px',
            "textAlign": 'center',
            "y": '10px'
        },
        "legend":{
            "x":"75%",
            "y":"25%",
            "border-width":1,
            "backgroundColor": 'none',
            "border-color":"white",
            "border-radius":"5px",
            "header":{
                "text":"Priority Types",
                "font-family":"Arial",
                "font-size":12,
                "font-color":"#ffffff",
                "font-weight":"normal"
            },
            "marker":{
                "type":"circle"
            },
            "toggle-action":"remove",
            "minimize":"true",
            "icon":{
                "line-color":"#ffffff"
            },
            "max-items":8,
            "overflow":"scroll"
        },
        "plotarea":{
            "margin-right":"30%",
            "margin-top":"15%"
        },
        "plot":{
            "animation":{
                "on-legend-toggle": "true",
                "effect": 5,
                "method": 1,
                "sequence": 1,
                "speed": 1
            },
            "value-box":{
                "text":"%v",
                "font-size":12,
                "font-family":"Arial",
                "font-weight":"normal",
                "placement":"out",
                "font-color":"#ffffff",
            },
            "tooltip":{
                "text":"%t: %v (%npv%)",
                "font-color":"black",
                "font-family":"Arial",
                "text-alpha":1,
                "background-color":"white",
                "alpha":0.7,
                "border-width":1,
                "border-color":"#cccccc",
                "line-style":"dotted",
                "border-radius":"10px",
                "padding":"10%",
                "placement":"node:center"
            },
            "border-width":1,
            "border-color":"#cccccc",
            "line-style":"dotted"
        },
        "series":[
            {
                "values":[buggie],
                "background-color":"#29B6F6",
                "legend-item": {
                    "font-color": "#ffffff"
                },
                "text":"Bug"
            },
            {
                "values":[featreq],
                "background-color":"#5FB83A",
                "legend-item": {
                    "font-color": "#ffffff"
                },
                "text":"Feature Request"
            },
            {
                "values":[custiss],
                "background-color":"#A50079",
                "legend-item": {
                    "font-color": "#ffffff"
                },
                "text":"Customer Issue"
            },
            {
                "values":[intcl],
                "background-color":"#FFA726",
                "legend-item": {
                    "font-color": "#ffffff"
                },
                "text":"Internal Cleanup"
            },
            {
                "values":[proc],
                "background-color":"#EF5350",
                "legend-item": {
                    "font-color": "#ffffff"
                },
                "text":"Process"
            },
            {
                "values":[vuln],
                "background-color":"#E53935",
                "legend-item": {
                    "font-color": "#ffffff"
                },
                "text":"Vulnerability"
            },
        ]
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
            "fontSize": "20px"
        },
        "backgroundColor": "#454754",
        "x": "34%",
        "y": "25%",
        "width": "30%",
        "height": "25%",
        "title": {
            "text": title,
            "paddingLeft": "20px",
            "paddingTop": "10px",
            "backgroundColor": "none",
            "fontColor": "#ffffff",
            "fontFamily": "Arial",
            "fontSize": "18px",
            "fontWeight": "normal",
            "height": "40px",
            "textAlign": "center",
            "y": "10px"
        },
        "plot": {
            "valueBox": {
            "text": "%v",
            "fontSize": "20x",
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
                "visible": "true"
            }
        },
        "tooltip": {
            "text":"Requests in WQ: %v",
            "font-color":"black",
            "font-family":"Arial",
            "text-alpha":1,
            "background-color":"white",
            "alpha":0.7,
            "border-width":1,
            "border-color":"#cccccc",
            "line-style":"dotted",
            "border-radius":"10px",
            "padding":"10%",
            "placement":"node:center"
        },
        "series": [
            {
            "values": dataColumns,
            "backgroundColor": "#ffffff",
            "indicator": [10, 5, 10, 10, 0.75],
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
################################################### Pie Chart - Request Priority ##################################################################################
################################################################################################################################################################
@login_required(login_url='/login/')
def zing_pie_requestpriority(request):

    #Workqueue Dataset Query
    workqueue_queryset = Bug.objects.raw("""    select 
                                                    1 as id,  
                                                    count(*) count, 
                                                    b.priority, '"'
                                                from bug_bug as b
                                                group by b.priority """)
    critical = 0
    urgent = 0
    medium = 0
    low = 0
    verylow = 0
    title = "Priority Types Pie Chart"

    #Workqueue Request Data
    for w in workqueue_queryset:
        if w.priority == "Critical":
            critical = w.count
        elif w.priority == "Urgent":
            urgent = w.count
        elif w.priority =="Medium":
            medium = w.count
        elif w.priority =="Low":
            low = w.count
        elif w.priority =="Very Low":
            verylow = w.count
        

    zingdata = {
        "type":"ring",
        "backgroundColor": "#454754",
        "x": "67%",
        "y": "25%",
        "width": "30%",
        "height": "25%",
        "title": {
            "text":title,
            "paddingLeft": '20px',
            "backgroundColor": 'none',
            "fontColor": '#ffffff',
            "fontFamily": 'Arial',
            "fontSize": '18px',
            "fontWeight": 'normal',
            "height": '40px',
            "textAlign": 'center',
            "y": '10px'
        },
        "images":[
            {
                "src":"https://s3bucketfortestwebsite.s3.amazonaws.com/bug.png",
                "width" : "4%",
                "height" : "4%",
                "offset-y" : -10
            }
        ],
        "legend":{
            "x":"75%",
            "y":"25%",
            "border-width":1,
            "backgroundColor": 'none',
            "border-color":"white",
            "border-radius":"5px",
            "header":{
                "text":"Priority Types",
                "font-family":"Arial",
                "font-size":12,
                "font-color":"#ffffff",
                "font-weight":"normal"
            },
            "marker":{
                "type":"circle"
            },
            "toggle-action":"remove",
            "minimize":"true",
            "icon":{
                "line-color":"#ffffff"
            },
            "max-items":8,
            "overflow":"scroll"
        },
        "plotarea":{
            "margin-right":"30%",
            "margin-top":"15%"
        },
        "plot":{
            "animation":{
                "on-legend-toggle": "true",
                "effect": 5,
                "method": 1,
                "sequence": 1,
                "speed": 1
            },
            "value-box":{
                "text":"%v",
                "font-size":12,
                "font-family":"Arial",
                "font-weight":"normal",
                "placement":"out",
                "font-color":"#ffffff",
            },
            "tooltip":{
                "text":"%t: %v (%npv%)",
                "font-color":"black",
                "font-family":"Arial",
                "text-alpha":1,
                "background-color":"white",
                "alpha":0.7,
                "border-width":1,
                "border-color":"#cccccc",
                "line-style":"dotted",
                "border-radius":"10px",
                "padding":"10%",
                "placement":"node:center"
            },
            "border-width":1,
            "border-color":"#cccccc",
            "line-style":"dotted"
        },
        "series":[
            {
                "values":[critical],
                "background-color":"#E53935",
                "legend-item": {
                    "font-color": "#ffffff"
                },
                "text":"Critical"
            },
            {
                "values":[urgent],
                "background-color":"#EF5350",
                "legend-item": {
                    "font-color": "#ffffff"
                },
                "text":"Urgent"
            },
            {
                "values":[medium],
                "background-color":"#FFA726",
                "legend-item": {
                    "font-color": "#ffffff"
                },
                "text":"Medium"
            },
            {
                "values":[low],
                "background-color":"#5FB83A",
                "legend-item": {
                    "font-color": "#ffffff"
                },
                "text":"Low"
            },
            {
                "values":[verylow],
                "background-color":"#29B6F6",
                "legend-item": {
                    "font-color": "#ffffff"
                },
                "text":"Very Low"
            },
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
                    "palette": ["#00ace6", "#0097A7"],
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
            "text": "%data-day:<br>%v requests <br>updated.",
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
                    "palette": ["#00ace6", "#0097A7"],
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

    pareto_requests     = zing_pareto_request(request)
    bar_workqueue      = zing_hbar_wqupdates(request) 
    pie_categorytypes   = zing_pie_requestcatagory(request)
    guage_requestcount  = zing_guage_requestcount(request)
    pie_prioritytypes   = zing_pie_requestpriority(request)
    cal_requests        = zing_cal_requests(request)
    cal_workqueue       = zing_cal_wqupdates(request)

    zingdata =  {
                "backgroundColor": "#454754",
                "layout": "2x2",
                "graphset":   [
                                pareto_requests, bar_workqueue, pie_categorytypes, guage_requestcount, pie_prioritytypes, cal_requests, cal_workqueue
                            ]
                }

    return JsonResponse(zingdata)




################################################### Deprecated #################################################################################################
################################################### Deprecated ###### Line Chart - Workqueue Updates ###########################################################
################################################### Deprecated #################################################################################################
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
