from django.contrib import admin
from .models import FeedItem, Feed

admin.site.register(Feed)
admin.site.register(FeedItem)
