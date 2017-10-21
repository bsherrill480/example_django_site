from django.db import models
from api.models import Master
from my_user.models import User
from django.dispatch import receiver
from safedelete.signals import pre_softdelete
# from feed.models import FeedItem
# I think we're running into a circular import problem with the models,
# just import Feed should fix the problem. Maybe find a more elegant solution?
import feed

# Post is a text post created by a user.
class Post(Master):
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='post')
    text = models.CharField(max_length=140)


# http://www.django-rest-framework.org/api-guide/authentication/#by-exposing-an-api-endpoint
# When a post is deleted, delete the corresponding feedItems.
@receiver(pre_softdelete, sender=Post)
def cascade_deletes(sender, instance=None, created=False, **kwargs):
    feed.models.FeedItem.objects.filter(post=instance).delete()

