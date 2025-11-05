from rest_framework import serializers
from apps.users.models import Feedback


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'user', 'rating', 'user_name', 'user_email', 'suggestion', 'type', 'status', 'reply', 'created_at']
        read_only_fields = ['id', 'user', 'user_name', 'user_email', 'type', 'status', 'reply', 'created_at']


class FeedbackCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['rating', 'suggestion']


class FeedbackReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['reply']
