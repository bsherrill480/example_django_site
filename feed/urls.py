from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from . import views


ROUTER = DefaultRouter()
ROUTER.register(r'', views.FeedItemViewSet, base_name='feed-item')

# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(ROUTER.urls)),
]
