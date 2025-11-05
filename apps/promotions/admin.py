from django.contrib import admin
from .models import Promotion


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ("title", "upc_id", "user", "category", "price", "status", "visibility", "start_date", "end_date")
    list_filter = ("status", "visibility", "category")
    search_fields = ("title", "upc_id", "user__email")
    date_hierarchy = "start_date"
