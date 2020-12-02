from django.urls import path, include
#import from import views
from rest_framework import routers
from api import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'buglistall', views.BugListAllViewSet)
router.register(r'buglistfiltered', views.BugListFilteredViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    path('workqueue-all/', views.json_bug_list_all, name='wq-all'),
    path('workqueue-filtered/', views.json_bug_list_wq, name='wq-filtered'),
    #path('bug-list/', views.BugsSerializer, name='bug-list'),
] 
