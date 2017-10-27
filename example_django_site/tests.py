from django.urls import reverse
from django.test import TestCase
from rest_framework import status


class RedirectTestCase(TestCase):
    def test_redirect(self):
        url = reverse('home')
        expected_redirect_to = reverse('docs:main_doc_view')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertTrue('location' in response)
        self.assertEqual(response['location'], expected_redirect_to)
