from rest_framework import serializers
from .models import Post
from my_user.models import User
from group.models import Group
from util.serializer_mixins import WriteOnceMixin


class PostSerializer(WriteOnceMixin, serializers.ModelSerializer):
    # to_group_id and to_user_id only for view, not model
    to_group_id = serializers.IntegerField(default=0, write_only=True, required=False)
    to_user_id = serializers.IntegerField(default=0, write_only=True, required=False)

    class Meta:
        model = Post
        fields = ('owner', 'text', 'to_group_id', 'to_user_id', 'id')
        extra_kwargs = {
            'id': {'read_only': True},
            'owner': {'read_only': True}
        }

    def _remove_view_fields_from_validated_data(self, validated_data):
        validated_data.pop('to_group_id', None)
        validated_data.pop('to_user_id', None)

    def create(self, validated_data):
        self._remove_view_fields_from_validated_data(validated_data)
        user = self.context['request'].user
        post = Post(owner=user, **validated_data)
        post.save()
        return post

    def update(self, instance, validated_data):
        self._remove_view_fields_from_validated_data(validated_data)
        return super(PostSerializer, self).update(instance, validated_data)

    def validate(self, attrs):
        method = self.context['request'].method
        # we only care about having to_group_id or to_user_id if it's a creating a new object
        if method == 'POST':
            to_group_id = attrs['to_group_id']
            to_user_id = attrs['to_user_id']
            # this works like XOR
            if bool(to_user_id) == bool(to_group_id):
                raise serializers.ValidationError("Must pass to_group_id XOR to_user_id")
            if to_group_id and not Group.objects.filter(pk=to_group_id).exists():
                    raise serializers.ValidationError("Invalid group")
            if to_user_id and not User.objects.filter(pk=to_user_id).exists():
                    raise serializers.ValidationError("Invalid User")
        return super(PostSerializer, self).validate(attrs)

