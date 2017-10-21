from django.conf.urls import url, include
from post import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'post', views.PostViewSet)


urlpatterns = [
    url(r'^', include(router.urls))
]

