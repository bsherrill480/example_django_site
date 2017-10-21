from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager as DefaultUserManager
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from api.models import Master
from safedelete.managers import SafeDeleteManager


class UserManager(SafeDeleteManager, DefaultUserManager):
    pass


class User(Master, AbstractUser):
    objects = UserManager()

    def __repr__(self):
        return str(self.username)


class FriendshipManager(SafeDeleteManager, models.Manager):
    # returns friendships where the user does not have a reciprocating friendship,
    # i.e. "pending approval"
    def get_pending_friendships_for_user(self, user):
        user_id = user.id if isinstance(user, User) else user
        translations = {
            'f1.creator_id': 'creator',
            'f1.friend_id': 'friend',
            'f1.id': 'id',
        }
        raw_qs = self.raw(
            """
            SELECT f1.creator_id, f1.friend_id, f1.id
            FROM my_user_friendship f1
            LEFT JOIN my_user_friendship f2 ON f1.friend_id = f2.creator_id
            WHERE f1.friend_id = %s AND f2.creator_id IS NULL
            """, params=[user_id], translations=translations)
        return raw_qs

    # returns friendships where the user does has a reciprocating friendship, i.e. they are friends
    def get_mutual_friendships_for_user(self, user):
        user_id = user.id if isinstance(user, User) else user
        translations = {
            'f1.creator_id': 'creator',
            'f1.friend_id': 'friend',
            'f1.id': 'id',
        }
        raw_qs = self.raw(
            """
            SELECT f1.creator_id, f1.friend_id, f1.id
            FROM my_user_friendship f1
            INNER JOIN my_user_friendship f2 ON f1.friend_id = f2.creator_id
            WHERE f1.creator_id = %s AND f2.friend_id = %s
            """, params=[user_id, user_id], translations=translations)
        return raw_qs


class Friendship(Master):
    class Meta:
        unique_together = ('creator', 'friend')

    def __repr__(self):
        return '({} :: {}->{})'.format(self.id, self.creator, self.friend)

    objects = FriendshipManager()

    creator = models.ForeignKey(User,
                                # on_delete=models.PROTECT,
                                related_name='friendship_creator_set')
    friend = models.ForeignKey(User,
                               # on_delete=models.PROTECT,
                               related_name='friend_set')


# http://www.django-rest-framework.org/api-guide/authentication/#by-exposing-an-api-endpoint
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
