from django.contrib import admin
from .models import Product, ProductCategory


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'created_at')
    search_fields = ('category_name',)
    ordering = ('category_name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'upc_id', 'user', 'category', 'type', 'price', 'offer_price', 'created_at')
    list_filter = ('type', 'category', 'created_at')
    search_fields = ('title', 'upc_id', 'user__email', 'category__category_name')
    autocomplete_fields = ('user', 'category')
    ordering = ('-created_at',)
