from rest_framework import serializers
from .models import User, Friendship
from util import serializer_mixins as sm
from django.db.utils import IntegrityError


# Serializers define the API representation.
class UserSerializer(sm.WriteOnceMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'id', 'password')
        write_once_fields = ('username',)
        extra_kwargs = {
            'id': {'read_only': True}
        }

    def validate_password(self, value):
        """
        Check the supplied password is valid
        """
        if not len(value):
            raise serializers.ValidationError("Password must have length greater than 0.")
        return value

    def create(self, validated_data):
        """
        When creating a user, let django deal with the password (i.e. hashing, salting, ...)
        """
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        instance = super(UserSerializer, self).update(instance, validated_data)
        if 'password' in validated_data:
            password = validated_data['password']
            instance.set_password(password)
            instance.save()
        return instance

    # never show password hash to user
    def to_representation(self, instance):
        representation = super(UserSerializer, self).to_representation(instance)
        if 'password' in representation:
            del representation['password']
        return representation


class FriendshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = ('creator', 'friend', 'id')
        extra_kwargs = {
            'creator': {'read_only': True},
            'id': {'read_only': True},
        }

    def create(self, validated_data):
        user = self.context['request'].user

        # Creating a second would violate unique constraint.
        try:
            friendship = Friendship.objects.get(creator=user, friend=validated_data['friend'])
        except Friendship.DoesNotExist:
            friendship = Friendship(creator=user, **validated_data)
            friendship.save()
        return friendship

