import uuid
from django.db import models
from django.utils import timezone


class FAQ(models.Model):
    TYPE_CHOICES = (
        (2, 'Reseller app'),
        (3, 'Store owner app'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(max_length=500)
    answer = models.TextField()
    type = models.IntegerField(choices=TYPE_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question[:50]
