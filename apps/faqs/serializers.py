from rest_framework import serializers
from .models import FAQ


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'type', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
