from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("heading", "user", "type", "read", "created_at")
    list_filter = ("type", "read", "created_at")
    search_fields = ("heading", "user__email", "content")
    date_hierarchy = "created_at"
