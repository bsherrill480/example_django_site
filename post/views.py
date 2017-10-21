# explicit imports are better than implicit
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from .serializers import PostSerializer
from .models import Post
from group.models import GroupMember
from feed.models import Feed, FeedItem


class PostViewSet(ModelViewSet):
    """
    API Endpoint containing information on facebook post object.

    create:
    Create a post.

    list:
    Returns all posts owned by the authenticated user.

    retrieve:
    Returns a specified post if it exists and is owned the authenticated user.

    update:
    Updates a post object if the user is authenticated and post is owned by the user.

    partial_update:
    Updates part of a post if it exists and is owned by the authenticated user.

    delete:
    Deletes a specified post if the user is authenticated and post is owned by the user.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Post.objects.all()
        else:
            return Post.objects.filter(owner=self.request.user)

    permission_classes = (permissions.IsAuthenticated, )

    # Create post for user or group
    def perform_create(self, serializer):
        # we know we have a valid user or group, since The serializer would raise an
        # exception if one was invalid
        post_instance = serializer.save()
        to_group_id = serializer.initial_data.get('to_group_id', None)
        to_user_id = serializer.initial_data.get('to_user_id', None)

        if to_group_id:
            self.perform_create_group_post(post_instance, to_group_id)
        elif to_user_id:
            self.perform_create_user_post(post_instance, to_user_id)

        return post_instance

    # To share post with a group, create feeditems with the given post instance for every group member
    def perform_create_group_post(self, post_instance, to_group_id):
        # prefetch related is just a query optimization
        # https://docs.djangoproject.com/en/1.11/ref/models/querysets/#prefetch-related
        group_members = GroupMember.objects.filter(group=to_group_id).prefetch_related('user__feed')
        for group_member in group_members:
            group_member_feed = group_member.user.feed
            feed_item = FeedItem(feed=group_member_feed, post=post_instance)
            feed_item.save()

    # To pst news to the feed, create a post by taking a user_id parameter and make a feeditem for this user
    def perform_create_user_post(self, post_instance, to_user_id):
        user_feed = Feed.objects.get(user=to_user_id)
        FeedItem.objects.create(feed=user_feed, post=post_instance)







