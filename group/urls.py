from django.conf.urls import url, include
from group import views
from rest_framework.routers import DefaultRouter


ROUTER = DefaultRouter()
ROUTER.register(r'group', views.GroupViewSet, base_name='group')
ROUTER.register(r'groupMember', views.GroupMemberViewSet, base_name='groupmember')


urlpatterns = [
    url(r'^', include(ROUTER.urls)),
]
