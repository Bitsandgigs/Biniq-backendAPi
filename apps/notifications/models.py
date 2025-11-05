import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings


class Notification(models.Model):
    TYPE_CHOICES = (
        ('reseller', 'Reseller'),
        ('store_owner', 'Store Owner'),
        ('all', 'All'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    heading = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.heading} -> {self.user.email}"
