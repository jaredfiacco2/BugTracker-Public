from django.urls import path
#import from import views
from bug import views
urlpatterns = [
	path('', views.bug_list_view, name='bug-list'),
    path('create/', views.bug_create_view , name='bug-create' ),
    path('create/success', views.bug_create_view , name='bug-create-success' ),
    path('<int:id>/', views.bug_detail_view, name='bug-detail'),
    path('<int:id>/update/', views.bug_update_view, name='bug-update'),
    path('<int:id>/delete/', views.bug_delete_view, name='bug-delete'),
    path('api/workqueue-all', views.json_bug_list_all, name='wq-all'),
    path('api/workqueue-filtered', views.json_bug_list_wq, name='wq-filtered'),
] 
