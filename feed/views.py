from rest_framework import viewsets, permissions
from .models import FeedItem
from .serializers import FeedItemSerializer


class FeedItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    list:
    Returns an feed for current authenticated user.

    retrieve:
    Returns a specific item from an authenticated user's feed.
    """
    def get_queryset(self):
        if self.request.user.is_superuser:
            return FeedItem.objects.all()
        else:
            user = self.request.user
            feed = user.feed
            feed_items = FeedItem.objects.filter(feed=feed)
            filter_user = self.request.GET.get('filter_user_id', None)
            if filter_user:
                feed_items = feed_items.filter(post__owner=filter_user)
            return feed_items

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FeedItemSerializer
