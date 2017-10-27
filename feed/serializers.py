from rest_framework import serializers
from post.serializers import PostSerializer
from .models import Feed, FeedItem


class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = ('user',)


class FeedItemSerializer(serializers.ModelSerializer):
    post = PostSerializer()

    class Meta:
        model = FeedItem
        fields = ('feed', 'post')
