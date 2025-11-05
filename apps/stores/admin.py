from django.contrib import admin
from .models import Store, StoreComment


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('store_name', 'user', 'likes', 'followers', 'views_count', 'verified', 'created_at')
    search_fields = ('store_name', 'user__email')
    list_filter = ('verified', 'created_at')


@admin.register(StoreComment)
class StoreCommentAdmin(admin.ModelAdmin):
    list_display = ('store', 'user_name', 'created_at')
    search_fields = ('store__store_name', 'user_name', 'content')
