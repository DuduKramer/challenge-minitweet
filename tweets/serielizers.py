from django.conf import settings
from rest_framework import serializers
from .models import Tweet

# Limite máximo do tweet vindo das configurações, com fallback padrão de 240 caracteres
MAX_TWEET_LENGTH = getattr(settings, 'MAX_TWEET_LENGTH', 240)

class TweetLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tweet
        fields = ['id', 'content', 'likes']

    def validate_actions(self, value):
        value = value.lower().strip()
        if value not in ['like', 'unlike']:
            raise serializers.ValidationError("This is not a valid action for Tweets.")
        return value

class TweetSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)  # Corrige o campo username

    class Meta:
        model = Tweet
        fields = ['id', 'content', 'likes', 'username']  # Inclui o campo username

    def get_likes(self, obj):
        return obj.likes.count()

    def validate_content(self, value):
        if len(value) > MAX_TWEET_LENGTH:
            raise serializers.ValidationError(
                f"Content exceeds {MAX_TWEET_LENGTH} characters limit."
            )
        return value