from django.urls import path
#import from import views
from bug import views
urlpatterns = [
	path('', views.bug_list_view, name='bug-wq'),
    path('create/', views.bug_create_view , name='bug-create' ),
    path('create/success', views.bug_create_view , name='bug-create-success' ),
    path('<int:id>/', views.bug_detail_view, name='bug-wqdetail'),
    path('<int:id>/update/', views.bug_update_view, name='bug-update'),
    path('<int:id>/delete/', views.bug_delete_view, name='bug-delete'),
    path('dashboard', views.bug_dashboard, name='bug-db'),
    path('zingdata-requests', views.zing_pareto_request, name='zingdata-requests'),
    path('zingdata-wqupdates', views.zing_line_wqupdates, name='zingdata-wqupdates'),
    path('zingdata-cal-wqupdates', views.zing_cal_wqupdates, name='zingdata-cal-wqupdates'),
    path('zingdata-cal-requests', views.zing_cal_requests, name='zingdata-cal-requests'),
    path('zingdata-dashboard', views.zing_dashboard, name='zingdata-dashboard'),
    # path('calendarconfig', views.zingchartConfig, name= 'bugdata-calendarconfig'),
] 
