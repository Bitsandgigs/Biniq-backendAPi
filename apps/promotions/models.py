import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings
from apps.products.models import ProductCategory


class Promotion(models.Model):
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    )
    VISIBILITY_CHOICES = (
        ('On', 'On'),
        ('Off', 'Off'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='promotions')
    category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT, related_name='promotions')
    title = models.CharField(max_length=255)
    description = models.TextField()
    upc_id = models.CharField(max_length=120, unique=True, null=True, blank=True)
    tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    offer_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    banner = models.ImageField(upload_to='promotions/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    visibility = models.CharField(max_length=3, choices=VISIBILITY_CHOICES, default='On')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.title} ({self.upc_id})"
