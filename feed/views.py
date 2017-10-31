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
        user = self.request.user
        feed = user.feed
        feed_items = FeedItem.objects.filter(feed=feed)
        return feed_items

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FeedItemSerializer
