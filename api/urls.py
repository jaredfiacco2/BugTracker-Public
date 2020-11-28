from django.urls import path
#import from import views
from api import views
urlpatterns = [
    path('workqueue-all/', views.json_bug_list_all, name='wq-all'),
    path('workqueue-filtered/', views.json_bug_list_wq, name='wq-filtered'),
    path('bug-list/', views.restApiBugList, name="api-buglist"),
] 
