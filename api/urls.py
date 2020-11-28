from django.urls import path, include
#import from import views
from rest_framework import routers
from api import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    path('workqueue-all/', views.json_bug_list_all, name='wq-all'),
    path('workqueue-filtered/', views.json_bug_list_wq, name='wq-filtered'),
    #path('bug-list/', views.restApiBugList, name="api-buglist"),
] 
