import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings


class ProductCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category_name = models.CharField(max_length=120, unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = 'Product Categories'
        ordering = ['category_name']

    def __str__(self):
        return self.category_name


class Product(models.Model):
    TYPE_CHOICES = (
        (1, 'Trending'),
        (2, 'Activity Feed'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT, related_name='products')
    title = models.CharField(max_length=255)
    description = models.TextField()
    upc_id = models.CharField(max_length=120, unique=True, null=True, blank=True)
    tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    offer_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    image_inner = models.URLField(null=True, blank=True)
    image_outer = models.URLField(null=True, blank=True)
    banner = models.ImageField(upload_to='products/', null=True, blank=True)
    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.upc_id})"
