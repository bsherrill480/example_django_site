from rest_framework import serializers
from util.serializer_mixins import WriteOnceMixin
from .models import *


class GroupSerializer(serializers.ModelSerializer, WriteOnceMixin):
    class Meta:
        model = Group
        fields = ['id', 'group_owner', 'name']
        write_once_fields = ('group_owner',)


class GroupMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMember
        fields = ['id', 'user', 'group']
