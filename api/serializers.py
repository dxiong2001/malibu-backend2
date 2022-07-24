from re import S
from rest_framework import serializers
from api.models import Tweet


class TweetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tweet
        fields=('_id', 'url', 'tweet')

