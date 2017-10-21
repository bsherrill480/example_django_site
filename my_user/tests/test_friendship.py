from ..models import Friendship
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from .util import UserTestUtil


class FriendshipTestCase(TestCase):
    def setUp(self):
        self.user_a = UserTestUtil.create_user()
        self.user_b = UserTestUtil.create_user()
        self.user_c = UserTestUtil.create_user()
        self.user_a_b_friendship = Friendship.objects.create(
            creator=self.user_a,
            friend=self.user_b
        )
        self.user_b_a_friendship = Friendship.objects.create(
            creator=self.user_b,
            friend=self.user_a
        )
        self.user_a_c_friendship = Friendship.objects.create(
            creator=self.user_a,
            friend=self.user_c
        )


class FriendshipManagerTestCase(FriendshipTestCase):
    def get_pending_friendships(self, user):
        pending_friendships_raw = Friendship.objects.get_pending_friendships_for_user(user)
        pending_friendships = [i for i in pending_friendships_raw]
        return pending_friendships

    def get_mutual_friendships(self, user):
        pending_friendships_raw = Friendship.objects.get_mutual_friendships_for_user(user)
        pending_friendships = [i for i in pending_friendships_raw]
        return pending_friendships

    def test_get_pending_friendships(self):
        a_pending_friendships = self.get_pending_friendships(self.user_a)
        self.assertEqual(len(a_pending_friendships), 0)
        c_pending_friendships = self.get_pending_friendships(self.user_c)
        self.assertEqual(len(c_pending_friendships), 1)
        c_pending_friendship = c_pending_friendships[0]
        self.assertEqual(c_pending_friendship.creator.id, self.user_a.id)
        self.assertEqual(c_pending_friendship.friend.id, self.user_c.id)

    def test_get_mutual_friendships(self):
        c_friendships = self.get_mutual_friendships(self.user_c)
        self.assertEqual(len(c_friendships), 0)

        b_friendships = self.get_mutual_friendships(self.user_b)
        self.assertEqual(len(b_friendships), 1)
        b_friendship = b_friendships[0]
        self.assertEqual(b_friendship.creator.id, self.user_b.id)
        self.assertEqual(b_friendship.friend.id, self.user_a.id)

        a_friendships = self.get_mutual_friendships(self.user_a)
        self.assertEqual(len(a_friendships), 1)
        a_friendship = a_friendships[0]
        self.assertEqual(a_friendship.creator.id, self.user_a.id)
        self.assertEqual(a_friendship.friend.id, self.user_b.id)


class PendingFriendshipAPITestCase(FriendshipTestCase):
    def test_anon(self):
        url = reverse('api:user:friendship-list-pending')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_has_pending(self):
        url = reverse('api:user:friendship-list-pending')
        self.client.login(
            username=self.user_c.username,
            password=UserTestUtil.DEFAULT_USER_PASSWORD
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [{'id': self.user_a_c_friendship.id,
                                          'creator': self.user_a_c_friendship.creator.id,
                                          'friend': self.user_a_c_friendship.friend.id}]
                         )

    def test_empty_pending(self):
        url = reverse('api:user:friendship-list-pending')
        self.client.login(
            username=self.user_a.username,
            password=UserTestUtil.DEFAULT_USER_PASSWORD
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])


class MutualFriendshipAPITestCase(FriendshipTestCase):
    def test_see_friends(self):
        url = reverse('api:user:friendship-list-mutual', kwargs={'user': self.user_a.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [{'id': self.user_a_b_friendship.id,
                                          'creator': self.user_a_b_friendship.creator.id,
                                          'friend': self.user_a_b_friendship.friend.id}]
                         )

    def test_see_friends_empty(self):
        url = reverse('api:user:friendship-list-mutual', kwargs={'user': self.user_c.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])


class DestroyFriendshipAPITestCase(FriendshipTestCase):
    def test_anon(self):
        url = reverse('api:user:friendship-detail', kwargs={'pk': self.user_a_c_friendship.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_is_owner_pending(self):
        user_a_c_friendship_id = self.user_a_c_friendship.id
        url = reverse('api:user:friendship-detail', kwargs={'pk': user_a_c_friendship_id})
        self.client.login(
            username=self.user_a.username,
            password=UserTestUtil.DEFAULT_USER_PASSWORD
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Friendship.objects.filter(id=user_a_c_friendship_id).count(), 0)

    # test deleting 1 friendship will delete both.
    def test_is_owner_mutual(self):
        user_a_b_friendship_id = self.user_a_b_friendship.id
        user_b_a_friendship_id = self.user_b_a_friendship.id
        url = reverse('api:user:friendship-detail', kwargs={'pk': user_a_b_friendship_id})
        self.client.login(
            username=self.user_a.username,
            password=UserTestUtil.DEFAULT_USER_PASSWORD
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Friendship.objects.filter(id=user_a_b_friendship_id).count(), 0)
        self.assertEqual(Friendship.objects.filter(id=user_b_a_friendship_id).count(), 0)


class CreateFriendshipAPITestCase(FriendshipTestCase):
    def test_anon(self):
        url = reverse('api:user:friendship-list')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_not_existing(self):
        url = reverse('api:user:friendship-list')
        self.client.login(
            username=self.user_c.username,
            password=UserTestUtil.DEFAULT_USER_PASSWORD
        )
        response = self.client.post(url, data={
            'friend': self.user_a.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Friendship.objects.filter(creator=self.user_c, friend=self.user_a).count(),
            1
        )

    def test_create_already_existing(self):
        url = reverse('api:user:friendship-list')
        self.client.login(
            username=self.user_a.username,
            password=UserTestUtil.DEFAULT_USER_PASSWORD
        )
        response = self.client.post(url, data={
            'friend': self.user_c.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Friendship.objects.filter(creator=self.user_a, friend=self.user_c).count(),
            1
        )

