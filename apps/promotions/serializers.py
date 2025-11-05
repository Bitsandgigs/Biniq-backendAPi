from rest_framework import serializers
from apps.products.models import ProductCategory
from .models import Promotion


class PromotionSerializer(serializers.ModelSerializer):
    category_id = serializers.UUIDField(write_only=True)
    category = serializers.SlugRelatedField(slug_field='category_name', read_only=True)

    class Meta:
        model = Promotion
        fields = [
            'id', 'user', 'category', 'category_id', 'title', 'description', 'upc_id',
            'tags', 'created_at', 'price', 'offer_price', 'banner', 'status', 'start_date', 'end_date', 'visibility', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_category_id(self, value):
        if not ProductCategory.objects.filter(id=value).exists():
            raise serializers.ValidationError('Category not found')
        return value

    def validate(self, attrs):
        start = attrs.get('start_date')
        end = attrs.get('end_date')
        if start and end and end < start:
            raise serializers.ValidationError({'end_date': 'End date must be after start date'})
        offer = attrs.get('offer_price')
        price = attrs.get('price')
        if offer is not None and price is not None and offer > price:
            raise serializers.ValidationError({'offer_price': 'Offer price cannot exceed price'})
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        category_id = validated_data.pop('category_id')
        category = ProductCategory.objects.get(id=category_id)
        return Promotion.objects.create(user=user, category=category, **validated_data)

    def update(self, instance, validated_data):
        category_id = validated_data.pop('category_id', None)
        if category_id:
            instance.category = ProductCategory.objects.get(id=category_id)
        return super().update(instance, validated_data)
