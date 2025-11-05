from rest_framework import serializers
from .models import Store, StoreComment


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = [
            'id', 'user', 'store_name', 'user_latitude', 'user_longitude', 'address', 'city', 'state',
            'zip_code', 'country', 'google_maps_link', 'website_url', 'working_days', 'working_time',
            'phone_number', 'store_email', 'facebook_link', 'instagram_link', 'twitter_link', 'whatsapp_link',
            'followers', 'likes', 'verified', 'store_image', 'ratings', 'rating_count', 'views_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'followers', 'likes', 'verified', 'ratings', 'rating_count', 'views_count', 'created_at', 'updated_at']


class StoreCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = [
            'store_name', 'user_latitude', 'user_longitude', 'address', 'city', 'state',
            'zip_code', 'country', 'google_maps_link', 'website_url', 'working_days', 'working_time',
            'phone_number', 'store_email', 'facebook_link', 'instagram_link', 'twitter_link', 'whatsapp_link',
            'store_image'
        ]

    def create(self, validated_data):
        validated_data.pop('user', None)  # Remove user if it exists
        return Store.objects.create(user=self.context['request'].user, **validated_data)



class StoreCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreComment
        fields = ['id', 'store', 'user', 'user_name', 'user_image', 'content', 'created_at']
        read_only_fields = ['id', 'store', 'user', 'user_name', 'user_image', 'created_at']
