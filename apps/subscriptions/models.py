import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings


class Plan(models.Model):
    TYPE_CHOICES = (
        ('reseller', 'Reseller'),
        ('store_owner', 'Store Owner'),
    )
    TIER_CHOICES = (
        ('tier1', 'Tier 1'),
        ('tier2', 'Tier 2'),
        ('tier3', 'Tier 3'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    tier = models.CharField(max_length=10, choices=TIER_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.PositiveIntegerField(help_text='Duration in days')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('type', 'tier')

    def __str__(self):
        return f"{self.type} {self.tier}"


class Subscription(models.Model):
    STATUS_CHOICES = (
        ('completed', 'Completed'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_id = models.CharField(max_length=32, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    user_name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=Plan.TYPE_CHOICES)
    plan = models.CharField(max_length=10, choices=Plan.TIER_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    date = models.DateTimeField(default=timezone.now)
    duration = models.PositiveIntegerField(help_text='Duration in days')

    card_number = models.CharField(max_length=16)
    cardholder_name = models.CharField(max_length=255)
    expiry_month = models.CharField(max_length=2)
    expiry_year = models.CharField(max_length=4)
    cvc = models.CharField(max_length=4)

    def __str__(self):
        return f"{self.order_id} - {self.user.email}"
