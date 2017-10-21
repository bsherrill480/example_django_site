import random
import string

from .models import Group, GroupMember
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from my_user.models import User


# Create your tests here.

class GroupTestCase(APITestCase):
    def setUp(self):
        self.a_user = User.objects.create_user('name', 'name@name.com', 'password')
        self.a_user.save()
        self.client.login(username='name', password='password')
        self.my_group = Group.objects.create(group_owner=self.a_user, name='family')
        self.my_group.save()

    @staticmethod
    def random_string():
        result = ''
        for i in range(7):
            result += (random.choice(string.ascii_lowercase + string.digits))
        return result

    @staticmethod
    def add_users(user_count):
        user_list = []
        for i in range(user_count):
            this_user = User(username=GroupTestCase.random_string(),
                             email=GroupTestCase.random_string(),
                             password=GroupTestCase.random_string())
            this_user.save()
            user_list.append(this_user)
        return user_list

    # Submits a post api call
    def create_instance(self):
        url = reverse('api:group:group-list')
        response = self.client.post(path=url, data=
        {
            'group_owner': self.a_user.id,
            'name': 'friends',
        })
        return response

    # Verifies correctness of post api call
    def test_create_instance(self):
        response = self.create_instance()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        group = Group.objects.get(name='friends')
        self.assertEqual(group.group_owner.id, self.a_user.id)
        self.assertEqual(group.name, 'friends')
        self.assertEqual(2, Group.objects.count())

    # Confirms permissions are correct for post api call
    def test_create_instance_unauthorized(self):
        self.client.logout()
        response = self.create_instance()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Submits get api call for collection
    def get_list(self):
        my_group_2 = Group.objects.create(group_owner=self.a_user, name='neighborhood')
        my_group_2.save()
        url = reverse('api:group:group-list')
        response = self.client.get(url)
        return response

    # Verifies correctness of api get call for collection
    def test_get_list(self):
        response = self.get_list()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(2, Group.objects.count())
        my_group_2 = Group.objects.get(name='neighborhood')
        ord_dict_list = response.data
        for ord_dict in ord_dict_list:
            self.assertEqual(self.a_user.id, ord_dict.get('group_owner'))
            group_name = ord_dict.get('name')
            self.assertTrue(group_name.__eq__(my_group_2.name) or group_name.__eq__(self.my_group.name))

    # Verifies correctness of api get call on instance
    def test_get_instance(self):
        url = reverse('api:group:group-detail', kwargs={'pk': self.my_group.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ord_dict = response.data
        self.assertEqual(ord_dict.get('group_owner'), self.a_user.id)

    # Verifies correctness of api put on collection
    def test_update_instance(self):
        url = reverse('api:group:group-detail', kwargs={'pk': self.my_group.id})
        response = self.client.put(path=url, data={'group_owner': self.my_group.group_owner.id,
                                                   'name': 'family'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ord_dict = response.data
        self.assertTrue(ord_dict.get('name').__eq__('family'))

    # Verifies that read only field is not updated
    def update_read_only(self):
        user_list = self.add_users(1)
        url = reverse('api:group:group-detail', kwargs={'pk': self.my_group.id})
        response = self.client.put(path=url, data={'group_owner': user_list[0].id,
                                                   'name': 'family'})
        self.assertEqual(self.a_user, self.my_group.group_owner)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    # Verifies permissions on api put on collection
    def test_update_instance_unauthorized(self):
        self.client.logout()
        url = reverse('api:group:group-detail', kwargs={'pk': self.my_group.id})
        response = self.client.put(path=url, data={'name': 'family'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_instance(self):
        url = reverse('api:group:group-detail', kwargs={'pk': self.my_group.id})
        response = self.client.patch(path=url, data={'name': 'family'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ord_dict = response.data
        self.assertTrue(ord_dict.get('name').__eq__('family'))

    # Verifies no collection update
    def test_update_list_not_supported(self):
        my_group_2 = Group(group_owner=User.objects.get(username='name'), name='co-workers')
        my_group_2.save()
        url = reverse('api:group:group-list')
        response = self.client.put(path=url, data={'name': 'family'})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # Verifies deletion on API for instances
    def test_delete_instance(self):
        url = reverse('api:group:group-detail', kwargs={'pk': self.my_group.id})
        response = self.client.delete(path=url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(0, Group.objects.count())

    # Verifies no collection delete
    def test_delete_instance_unauthorized(self):
        self.client.logout()
        url = reverse('api:group:group-detail', kwargs={'pk': self.my_group.id})
        response = self.client.delete(path=url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class GroupMemberTestCase(GroupTestCase):
    def setUp(self):
        super().setUp()
        self.my_group_member = GroupMember.objects.create(user=self.a_user, group=self.my_group)
        self.my_group_member.save()

    def test_get_instance(self):
        url = reverse('api:group:groupmember-detail', kwargs={'pk': self.my_group_member.id})
        response = self.client.get(url)
        a_dict = response.data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(a_dict.get('user'), self.a_user.id)
        self.assertEqual(a_dict.get('group'), self.my_group.id)

    def test_get_instance_unauthorized(self):
        self.client.logout()
        url = reverse('api:group:groupmember-detail', kwargs={'pk': self.my_group_member.id})
        response = self.client.get(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    @staticmethod
    def add_group_member_record():
        user2 = User.objects.create_user('user2', 'user2@user.com', 'password')
        user2.save()
        my_group_2 = Group.objects.create(group_owner=user2, name='dogs')
        my_group_2.save()
        my_group_member_2 = GroupMember.objects.create(user=user2, group=my_group_2)
        my_group_member_2.save()
        return my_group_2

    def test_get_list(self):
        my_group_2 = self.add_group_member_record()
        url = reverse('api:group:groupmember-list')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        dict_list = response.data
        for dict in dict_list:
            self.assertEqual(self.a_user.id, dict.get('user'))
            self.assertTrue(self.my_group.id == dict.get('group') or my_group_2.id == dict.get('group'))

    def test_get_list_unauthorized(self):
        self.client.logout()
        self.add_group_member_record()
        url = reverse('api:group:groupmember-list')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_membership(self):
        user_list = GroupMemberTestCase.add_users(5)
        for user in user_list:
            GroupMember(user=user, group=self.my_group).save()
        url = reverse('api:group:group-members-by-group', kwargs={'pk': self.my_group.id})
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        dict_list = response.data
        self.assertEqual(6, len(dict_list))
        for dict_item in dict_list:
            some_user = User.objects.get(pk=dict_item.get('user'))
            self.assertTrue(some_user in user_list or some_user.__eq__(self.a_user))

    def test_membership_unauthorized(self):
        self.client.logout()
        user_list = GroupMemberTestCase.add_users(5)
        for user in user_list:
            GroupMember(user=user, group=self.my_group).save()
        url = reverse('api:group:group-members-by-group', kwargs={'pk': self.my_group.id})
        response = self.client.get(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_delete_instance(self):
        url = reverse('api:group:groupmember-detail', kwargs={'pk': self.my_group_member.id})
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(0, GroupMember.objects.count())

    def test_delete_nonSelf_members(self):
        user_list = GroupTestCase.add_users(9)
        another_group = Group(group_owner=self.a_user, name='more_friends')
        another_group.save()
        url = reverse('api:group:groupmember-list')
        member_list = []
        for user in user_list:
            coin_flip = random.randint(1, 1000) % 2 == 0
            resp = self.client.post(path=url, data={
                'user': user.id,
                'group': self.my_group.id if coin_flip else another_group.id
            })
            self.assertEqual(status.HTTP_201_CREATED, resp.status_code)
            member_list.append(resp.data['id'])
        self.assertEqual(10, GroupMember.objects.filter(group_id__in=[self.my_group.id, another_group.id]).count())
        for member in member_list:
            url = reverse('api:group:groupmember-detail',
                          kwargs={'pk': member})
            response = self.client.delete(path=url)
            self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(1, GroupMember.objects.filter(group_id__in=[self.my_group.id, another_group.id]).count())

    def test_delete_instance_unauthorized(self):
        self.client.logout()
        url = reverse('api:group:groupmember-detail', kwargs={'pk': self.my_group_member.id})
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_create_instance(self):
        user2 = User.objects.create_user('user2', 'user2@user.com', 'password')
        user2.save()
        my_group_2 = Group.objects.create(group_owner=user2, name='dogs')
        my_group_2.save()
        url = reverse('api:group:groupmember-list')
        response = self.client.post(url, {
            'user': user2.id,
            'group': my_group_2.id,
        })
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(2, GroupMember.objects.count())

    def test_cascade_delete(self):
        self.test_membership()
        self.my_group.delete()
        self.assertEqual(0, GroupMember.objects.count())
