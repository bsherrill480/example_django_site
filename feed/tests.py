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
        self.a_feed = Feed.objects.get(user=self.a_user)
        self.post_1 = Post.objects.create(owner=self.b_user, text='hello world')
        self.feeditem1 = FeedItem.objects.create(feed=self.a_feed, post=self.post_1)
        self.post_2 = Post.objects.create(owner=self.b_user, text='hello world2')
        self.feeditem2 = FeedItem.objects.create(feed=self.a_feed, post=self.post_2)

    @staticmethod
    def post_to_expected(post):
        return {
            'id': post.id,
            'owner': post.owner.id,
            'text': post.text
        }


class FeedItemCollectionTestCase(FeedItemTestCase):
    def test_create_feeditem(self):
        self.client_login_a_user()
        url = reverse('api:feed:feed-item-list')
        data = {'feed': self.a_feed.id, 'post': self.post_1.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_feeditems(self):
        self.client_login_a_user()
        url = reverse('api:feed:feed-item-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        expected_data = [
            {'feed': self.a_feed.id, 'post': self.post_to_expected(self.post_1)},
            {'feed': self.a_feed.id, 'post': self.post_to_expected(self.post_2)},
        ]
        data = response.json()
        self.assertEqual(data, expected_data)

    def test_get_feeditem_with_invalid_permission(self):
        """
        To test that an unauthorized user should not see any feed.
        """
        url = reverse('api:feed:feed-item-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FeedItemElementTestCase(FeedItemTestCase):
    def test_delete_feeditem(self):
        self.client_login_a_user()
        url = reverse('api:feed:feed-item-detail', kwargs={'pk': self.feeditem1.id})
        data = {'feed': self.a_feed.id, 'post': self.post_1.id}
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_feeditem(self):
        self.client_login_a_user()
        url = reverse('api:feed:feed-item-detail', kwargs={'pk': self.feeditem1.id})
        data = {'feed': self.a_feed.id, 'post': self.post_1.id}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_feeditem(self):
        self.client_login_a_user()
        url = reverse('api:feed:feed-item-detail', kwargs={'pk': self.feeditem1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['feed'], self.a_feed.id)
        self.assertEqual(response.data['post'], self.post_to_expected(self.post_1))

