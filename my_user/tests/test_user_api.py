# from django.test import TestCase
from ..models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .util import UserTestUtil


class UserTestCase(APITestCase):
    def setUp(self):
        super(UserTestCase, self).setUp()
        self.a_user = UserTestUtil.create_user()
        self.b_user = UserTestUtil.create_user()

    def client_login_a_user(self):
        self.client.login(
            username=self.a_user.username,
            password=UserTestUtil.DEFAULT_USER_PASSWORD
        )


class UserCollectionTestCase(UserTestCase):
    def test_retrieve_with_cred(self):
        self.client_login_a_user()
        url = reverse('api:user:user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'user-list-cred-200')
        self.assertEqual(response.data, [{'id': self.a_user.id,
                                          'username': self.a_user.username,
                                          'email': self.a_user.email}],
                         'user-list-cred-response')

    def test_retrieve_anon(self):
        url = reverse('api:user:user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'user-list-anon-200')
        self.assertEqual(response.data, [],
                         'user-list-anon-response')

    def test_create(self):
        url = reverse('api:user:user-list')
        response = self.client.post(url, {
            'username': 'b',
            'password': 'b',
            'email': 'b@b.com'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'user-list-anon-200')
        user_b = User.objects.get(username='b')
        self.assertEqual(user_b.email, 'b@b.com')
        self.assertTrue(user_b.check_password('b'))


class UserElementTestCase(UserTestCase):
    def test_retrieve_valid_permission(self):
        self.client_login_a_user()
        url = reverse('api:user:user-detail', kwargs={'pk': self.a_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'user-detail-cred-200')
        self.assertEqual(response.data, {'id': self.a_user.id,
                                         'username': self.a_user.username,
                                         'email': self.a_user.email},
                         'user-list-cred-response')

    def test_retrieve_invalid_permission(self):
        url = reverse('api:user:user-list')
        response = self.client.get(url, kwargs={'pk': self.a_user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'user-detail-anon-200')
        self.assertEqual(response.data, [],
                         'user-list-anon-response')

    def test_update_valid_permission(self):
        url = reverse('api:user:user-detail', kwargs={'pk': self.a_user.id})
        initial_username = self.a_user.username
        self.client_login_a_user()
        response = self.client.put(url, {
            'password': 'c',
            'email': 'c@c.com',
            'username': 'foo'  # should be ignored if sent
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'user-detail-anon-200')
        a_user = User.objects.get(id=self.a_user.id)
        self.assertEqual(a_user.email, 'c@c.com')
        self.assertEqual(a_user.username, initial_username)
        self.assertTrue(a_user.check_password('c'))

    def test_update_invalid_permission(self):
        url = reverse('api:user:user-detail', kwargs={'pk': self.a_user.id})
        a_user_init_email = self.a_user.email
        response = self.client.put(url, {
            'password': 'c',
            'email': 'c@c.com',
        })
        # 404 because we're filtering queryset to just the client's user
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, 'user-detail-anon-200')
        a_user = User.objects.get(id=self.a_user.id)
        self.assertEqual(a_user.email, a_user_init_email)
        self.assertTrue(a_user.check_password(UserTestUtil.DEFAULT_USER_PASSWORD))

    def test_delete_logged_in(self):
        a_user_id = self.a_user.id
        url = reverse('api:user:user-detail', kwargs={'pk': a_user_id})
        self.client_login_a_user()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT,
                         'user-detail-delete')
        # `get` will throw error if a_user doesn't exist
        a_user_count = User.objects.filter(id=a_user_id).count()
        self.assertEqual(a_user_count, 0)

    def test_delete_logged_wrong_user(self):
        a_user_id = self.a_user.id
        b_user_id = self.b_user.id
        url = reverse('api:user:user-detail', kwargs={'pk': b_user_id})
        self.client_login_a_user()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND,
                         'user-detail-delete')
        # `get` will throw error if a_user doesn't exist
        a_user_count = User.objects.filter(id=a_user_id).count()
        self.assertEqual(a_user_count, 1)
        b_user_count = User.objects.filter(id=b_user_id).count()
        self.assertEqual(b_user_count, 1)
