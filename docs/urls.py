from django.conf.urls import url
from .views import MainDocView

urlpatterns = [
    url(r'^$', MainDocView.as_view(), name='main_doc_view'),
]
