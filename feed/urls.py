"""
urls.py for feed module.
"""
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from . import views


def get_router():
    """
    Create feed router and register our viewsets with it.
    :return: rest_framework router
    """
    router = DefaultRouter()
    router.register(r'', views.FeedItemViewSet, base_name='feed_item')
    return router

# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(get_router().urls)),
]
