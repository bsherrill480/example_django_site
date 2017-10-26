"""
serializers for feed module.
"""
from rest_framework import serializers
from post.serializers import PostSerializer
from .models import Feed, FeedItem


class FeedSerializer(serializers.ModelSerializer):
    """
    Feed Serializer
    """
    class Meta:
        model = Feed
        fields = ('user',)


class FeedItemSerializer(serializers.ModelSerializer):
    """
    FeedItem Serializer
    """
    post = PostSerializer()

    class Meta:
        model = FeedItem
        fields = ('feed', 'post')
