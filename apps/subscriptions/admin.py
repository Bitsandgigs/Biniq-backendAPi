from django.contrib import admin
from .models import Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("type", "tier", "amount", "duration", "updated_at")
    list_filter = ("type", "tier")
    search_fields = ("type", "tier")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "order_id",
        "user",
        "type",
        "plan",
        "amount",
        "status",
        "date",
        "duration",
    )
    list_filter = ("status", "type", "plan", "date")
    search_fields = ("order_id", "user__email", "user_name")
    date_hierarchy = "date"
