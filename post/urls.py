from django.conf.urls import url, include
from post import views
from rest_framework.routers import DefaultRouter

ROUTER = DefaultRouter()
ROUTER.register(r'post', views.PostViewSet)


urlpatterns = [
    url(r'^', include(ROUTER.urls))
]
