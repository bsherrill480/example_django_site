from django.conf.urls import url, include

urlpatterns = [
    url(r'^user/', include('my_user.urls', namespace='user')),
    url(r'^group/', include('group.urls', namespace='group')),
    url(r'^post/', include('post.urls', namespace='post')),
    url(r'^feed/', include('feed.urls', namespace='feed')),
]
