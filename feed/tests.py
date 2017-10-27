from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from my_user.models import User
from my_user.tests.util import UserTestUtil, AUserBUserMixin
from post.models import Post
from .models import Feed, FeedItem


class FeedModelTestCase(TestCase):
    def test_feed_on_user_creation(self):
        """
        Test that a feed is made when a user is created.
        """
        user = User.objects.create_user('test_user1', 'test_user1@email.com', 'password')
        feed_exists = Feed.objects.filter(user=user)
        self.assertTrue(feed_exists)


class FeedItemTestCase(AUserBUserMixin, APITestCase):
    def setUp(self):
        super(FeedItemTestCase, self).setUp()
        self.feed1 = Feed.objects.get(user=self.a_user)
        self.post_sample = Post.objects.create(owner=self.b_user, text='hello world')
        self.feeditem1 = FeedItem.objects.create(feed=self.feed1, post=self.post_sample)


class FeedItemCollectionTestCase(FeedItemTestCase):
    def test_create_feeditem(self):
        self.client_login_a_user()
        url = reverse('api:feed:feed-item-list')
        data = {'feed': self.feed1.id, 'post': self.post_sample.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class FeedItemElementTestCase(FeedItemTestCase):
    def test_delete_feeditem(self):
        self.client_login_a_user()
        url = reverse('api:feed:feed-item-detail', kwargs={'pk': self.feeditem1.id})
        data = {'feed': self.feed1.id, 'post': self.post_sample.id}
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_feeditem(self):
        self.client_login_a_user()
        url = reverse('api:feed:feed-item-detail', kwargs={'pk': self.feeditem1.id})
        data = {'feed': self.feed1.id, 'post': self.post_sample.id}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_feeditem_valid_permission(self):
        """
        To test that an user can only see its own feeditems.
        """
        self.client_login_a_user()
        url = reverse('api:feed:feed-item-detail', kwargs={'pk': self.feeditem1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, FeedItem.objects.count())
        self.assertEqual(response.data['feed'], self.feed1.id)
        self.assertEqual(
            response.data['post'],
            {
                'id': self.post_sample.id,
                'owner': self.post_sample.owner.id,
                'text': self.post_sample.text
            }
        )

    def test_get_feeditem_with_invalid_permission(self):
        """
        To test that an unauthorized user should not see any feed.
        """
        url = reverse('api:feed:feed-item-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
