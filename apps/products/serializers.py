from rest_framework import serializers
from .models import Product, ProductCategory


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'category_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    category_id = serializers.UUIDField(write_only=True)
    category = ProductCategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'user', 'category', 'category_id', 'title', 'description', 'upc_id',
            'tags', 'created_at', 'price', 'offer_price', 'banner', 'image_inner', 'image_outer',
            'type', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_type(self, value):
        if value not in (1, 2):
            raise serializers.ValidationError('Type must be 1 (Trending) or 2 (Activity Feed)')
        return value

    def validate(self, attrs):
        # Ensure category exists
        category_id = attrs.get('category_id')
        if category_id and not ProductCategory.objects.filter(id=category_id).exists():
            raise serializers.ValidationError({'category_id': 'Category not found'})
        price = attrs.get('price')
        offer = attrs.get('offer_price')
        if offer is not None and price is not None and offer > price:
            raise serializers.ValidationError({'offer_price': 'Offer price cannot exceed price'})
        return attrs

    def create(self, validated_data):
        category_id = validated_data.pop('category_id')
        category = ProductCategory.objects.get(id=category_id)
        user = self.context['request'].user
        product = Product.objects.create(category=category, user=user, **validated_data)
        return product

    def update(self, instance, validated_data):
        category_id = validated_data.pop('category_id', None)
        if category_id:
            try:
                instance.category = ProductCategory.objects.get(id=category_id)
            except ProductCategory.DoesNotExist:
                raise serializers.ValidationError({'category_id': 'Category not found'})
        return super().update(instance, validated_data)
