from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Feedback


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ('email',)
    list_display = ('email', 'full_name', 'role', 'is_active', 'is_staff', 'verified')
    list_filter = ('role', 'is_active', 'verified', 'is_staff')
    search_fields = ('email', 'full_name')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {
            'fields': (
                'full_name', 'store_name', 'dob', 'gender', 'phone_number', 'address',
                'expertise_level', 'profile_image',
            )
        }),
        ('Subscription & Promotions', {
            'fields': (
                'subscription', 'subscription_end_time', 'total_promotions', 'used_promotions',
                'total_scans'
            )
        }),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'role', 'password1', 'password2'),
        }),
    )

    readonly_fields = ('created_at', 'updated_at')


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('suggestion', 'user__email')
    list_filter = ('created_at',)
