from django.conf import settings
from rest_framework import serializers
from .models import Tweet

MAX_TWEET_LENGTH = getattr(settings, 'MAX_TWEET_LENGTH', 240)  # fallback 240

class TweetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tweet
        fields = ['content']

    def validate_content(self, value):
        if len(value) > MAX_TWEET_LENGTH:
            raise serializers.ValidationError(f"Content exceeds {MAX_TWEET_LENGTH} characters limit.")
        return value
