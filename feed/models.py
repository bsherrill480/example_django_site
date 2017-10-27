from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from my_user.models import User
from post.models import Post
from api.models import Master


# Feed is a collection of FeedItems
class Feed(Master):
    user = models.OneToOneField(User,
                                on_delete=models.PROTECT)


class FeedItem(Master):
    feed = models.ForeignKey(Feed,
                             on_delete=models.PROTECT,
                             related_name='feed_set')
    post = models.ForeignKey(Post,
                             on_delete=models.PROTECT,
                             related_name='post_set')


# When a user is created, make a feed for them
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_feed_for_user(sender, instance=None, created=False, **kwargs):
    """
    makes a feed for user.
    """
    # pylint: disable=unused-argument
    if created:
        Feed.objects.create(user=instance)
