
# should be able to show all the FeedItems in a Feed
from django.shortcuts import render
from my_user.models import User


# display all the feeds for an user.
# def feed_view(request):
#    feed = User.feed
#    feed_item_list = feed.feed_item_set.all()
#    context = {'feed_item_list': feed_item_list}
#    return render(request, 'feed/index.html', context)

from .serializers import *
from rest_framework import viewsets, permissions
from rest_framework import generics


# class FeedView(generics.RetrieveAPIView):
#     """
#     A Feed is an collection of FeedItems, used only internally.
#
#     get:
#     Returns feed of specified user.
#     """
#     def get_queryset(self):
#         if self.request.user.is_superuser:
#             return Feed.objects.all()
#         else:
#             return Feed.objects.filter(user=self.request.user.id)
#
#     permission_classes = (permissions.IsAuthenticated, )
#     serializer_class = FeedSerializer


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
