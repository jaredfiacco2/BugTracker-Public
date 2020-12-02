from django.urls import path, include
# #import from import views
# from rest_framework import routers
from api import views

# router = routers.DefaultRouter()
# router.register(r'users', views.UserViewSet)
# router.register(r'groups', views.GroupViewSet)
# router.register(r'buglist', views.BugsSerializer)

urlpatterns = [
    # path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('users', views.UserViewSet, name='api_users'),
    path('groups', views.GroupViewSet, name='api_groups'),
    path('buglist', views.BugsSerializer, name='api_buglist'),
    path('workqueue-all/', views.json_bug_list_all, name='api_wq-all'),
    path('workqueue-filtered/', views.json_bug_list_wq, name='api_wq-filtered'),
] 
