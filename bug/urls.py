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
    path('zingdata-requests', views.zing_line_request, name='zingdata-requests'),
    path('zingdata-wqupdates', views.zing_line_wqupdates, name='zingdata-wqupdates'),
    # path('calendarconfig', views.zingchartConfig, name= 'bugdata-calendarconfig'),
] 
