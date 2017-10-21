from django.urls import reverse
from .models import Post
from my_user.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from my_user.tests.util import UserTestUtil
from group.models import Group, GroupMember
from feed.models import FeedItem


class PostTestCase(APITestCase):
    def setUp(self):
        self.user1 = UserTestUtil.create_user()
        self.user2 = UserTestUtil.create_user()
        # setup group user
        self.g_user1 = UserTestUtil.create_user()
        self.group = Group.objects.create(group_owner=self.user1, name='foo')
        self.g_user1_gm = GroupMember.objects.create(group=self.group, user=self.g_user1)
        self.default_post_owner = self.user1
        self.default_post_text = 'hello world'

    def make_list_post(self, additional_data=None):
        if additional_data is None:
            # so we don't always to have to pass data if we know the post will be bad
            additional_data = {'to_user_id': self.user2.id}
        url = reverse('api:post:post-list')
        data_base = {'owner': self.default_post_owner.id, 'text': self.default_post_text}
        data = dict()
        data.update(additional_data)
        data.update(data_base)
        response = self.client.post(url, data, format='json')
        return response

    def default_login(self):
        self.client.login(
            username=self.default_post_owner.username,
            password=UserTestUtil.DEFAULT_USER_PASSWORD
        )

    def do_test_success_response(self, response, expected_status=status.HTTP_201_CREATED):
        post = response.data['id']
        self.assertEqual(response.status_code, expected_status)
        self.assertEqual(response.data['text'], self.default_post_text)
        self.assertEqual(response.data['owner'], self.default_post_owner.id)
        self.assertTrue(post)
        return post


class ListPostTestCase(PostTestCase):
    def test_create_post_group(self):
        self.default_login()
        response = self.make_list_post({'to_group_id': self.group.id})
        post = self.do_test_success_response(response)
        post_exists = Post.objects.filter(id=post).exists()
        self.assertTrue(post_exists)
        # check groups users feed was updated
        feed_items = FeedItem.objects.filter(feed__user=self.g_user1)
        feed_items_count = len(feed_items)
        self.assertEqual(feed_items_count, 1)
        feed_item = feed_items[0]
        self.assertEqual(feed_item.post.id, post)

    def test_create_post_user(self):
        self.default_login()
        response = self.make_list_post({'to_user_id': self.user2.id})
        post = self.do_test_success_response(response)
        post_exists = Post.objects.filter(id=post).exists()
        self.assertTrue(post_exists)
        # check groups users feed was updated
        feed_items = FeedItem.objects.filter(feed__user=self.user2)
        feed_items_count = len(feed_items)
        self.assertEqual(feed_items_count, 1)
        feed_item = feed_items[0]
        self.assertEqual(feed_item.post.id, post)

    def test_create_post_unauthorized(self):
        self.client.logout()
        response = self.make_list_post()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(0, Post.objects.count())

    # test list functionality
    def test_get_posts_by_user(self):
        user1_post = Post.objects.create(owner=self.user1, text='foo')
        Post.objects.create(owner=self.user2, text='foo')
        self.default_login()
        url = reverse('api:post:post-list')
        response = self.client.get(url)
        self.assertEqual(len(response.data), 1)
        post = response.data[0]
        self.assertEqual(post['text'], user1_post.text)
        self.assertEqual(post['owner'], user1_post.owner.id)
        self.assertEqual(post['id'], user1_post.id)


class DetailPostTestCase(PostTestCase):
    def test_delete_post(self):
        self.default_login()
        response = self.make_list_post({'to_user_id': self.user2.id})
        post = self.do_test_success_response(response)
        url = reverse('api:post:post-detail', kwargs={'pk': post})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        post_exists = Post.objects.filter(id=post).exists()
        self.assertFalse(post_exists)

        user_2_feed_items_count = FeedItem.objects.filter(feed__user=self.user2).count()
        self.assertEqual(user_2_feed_items_count, 0)

    def test_delete_post_unauthorized(self):
        self.default_login()
        response = self.make_list_post({'to_user_id': self.user2.id})
        post = self.do_test_success_response(response)
        url = reverse('api:post:post-detail', kwargs={'pk': post})
        self.client.logout()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_post(self):
        self.default_login()
        make_response = self.make_list_post({'to_user_id': self.user2.id})
        post = self.do_test_success_response(make_response)
        url = reverse('api:post:post-detail', kwargs={'pk': post})
        get_response = self.client.get(url)
        self.do_test_success_response(get_response, status.HTTP_200_OK)
        self.assertEqual(post, get_response.data['id'])

    def test_get_post_unauthorized(self):
        self.default_login()
        make_response = self.make_list_post({'to_user_id': self.user2.id})
        post = self.do_test_success_response(make_response)
        url = reverse('api:post:post-detail', kwargs={'pk': post})
        self.client.logout()
        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_post(self):
        self.default_login()
        new_text = 'foobar'
        make_response = self.make_list_post({'to_user_id': self.user2.id})
        post = self.do_test_success_response(make_response)
        url = reverse('api:post:post-detail', kwargs={'pk': post})
        update_response = self.client.put(url, dict({
            'text': new_text,
            'id': post
        }))
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        post = Post.objects.get(id=post)
        self.assertEqual(post.text, new_text)

    # I don't think this test is necesasry, since we can trust DRF, but doesn't hurt
    def test_update_post_try_to_change_owner(self):
        self.default_login()
        make_response = self.make_list_post({'to_user_id': self.user2.id})
        post = self.do_test_success_response(make_response)
        url = reverse('api:post:post-detail', kwargs={'pk': post})
        update_response = self.client.put(url, dict({
            'text': 'foo',
            'id': post,
            'owner': self.user2.id
        }))
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        post = Post.objects.get(id=post)
        self.assertEqual(post.owner, self.user1)  # owner did not change

    def test_update_invalid_cred(self):
        self.default_login()
        make_response = self.make_list_post({'to_user_id': self.user2.id})
        post = self.do_test_success_response(make_response)
        url = reverse('api:post:post-detail', kwargs={'pk': post})
        self.client.logout()
        update_response = self.client.put(url, dict({
            'text': 'foo',
            'id': post,
            'owner': self.user2.id
        }))
        self.assertEqual(update_response.status_code, status.HTTP_401_UNAUTHORIZED)
