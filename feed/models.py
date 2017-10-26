"""
models for feed module.
"""
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from my_user.models import User
from post.models import Post
from api.models import Master


# Feed is a collection of FeedItems
class Feed(Master):
    """
    Feed Model
    """
    user = models.OneToOneField(User,
                                on_delete=models.PROTECT)


# A FeedItem contains two pointers, one to a Feed and
# one to a Post.
class FeedItem(Master):
    """
    Feed Item Model
    """
    feed = models.ForeignKey(Feed,
                             on_delete=models.PROTECT,
                             related_name='feed_set')
    post = models.ForeignKey(Post,
                             on_delete=models.PROTECT,
                             related_name='post_set')

    def __repr__(self):
        return 'FeedItem: feed_id: {} post: {}'.format(self.feed.id, self.post.id)


# When a user is created, make a feed for them
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_feed_for_user(sender, instance=None, created=False, **kwargs):
    """
    When a user is created, make a feed for that user.
    """
    # pylint: disable=unused-argument
    if created:
        Feed.objects.create(user=instance)
