from django.contrib import admin
from .models import FAQ


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "type", "created_at")
    list_filter = ("type",)
    search_fields = ("question", "answer")
    date_hierarchy = "created_at"
