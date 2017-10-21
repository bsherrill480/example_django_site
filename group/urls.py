from django.conf.urls import url, include
from group import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'group', views.GroupViewSet, base_name='group')
router.register(r'groupMember', views.GroupMemberViewSet, base_name='groupmember')


urlpatterns = [
    url(r'^', include(router.urls)),
]
