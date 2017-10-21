from rest_framework import serializers
from .models import *
from post.serializers import PostSerializer


class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = ('user',)


class FeedItemSerializer(serializers.ModelSerializer):
    post = PostSerializer()
    class Meta:
        model = FeedItem
        fields = ('feed', 'post')
