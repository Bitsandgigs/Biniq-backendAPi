import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings


class Store(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='store')
    store_name = models.CharField(max_length=255)

    user_latitude = models.FloatField(null=True, blank=True)
    user_longitude = models.FloatField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=120, null=True, blank=True)
    state = models.CharField(max_length=120, null=True, blank=True)
    zip_code = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=120, null=True, blank=True)

    google_maps_link = models.URLField(null=True, blank=True)
    website_url = models.URLField(null=True, blank=True)
    working_days = models.CharField(max_length=120, null=True, blank=True)
    working_time = models.CharField(max_length=120, null=True, blank=True)
    phone_number = models.CharField(max_length=30, null=True, blank=True)
    store_email = models.EmailField(null=True, blank=True)

    facebook_link = models.URLField(null=True, blank=True)
    instagram_link = models.URLField(null=True, blank=True)
    twitter_link = models.URLField(null=True, blank=True)
    whatsapp_link = models.URLField(null=True, blank=True)

    followers = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    verified = models.BooleanField(default=False)
    store_image = models.URLField(null=True, blank=True)
    ratings = models.FloatField(default=0)
    rating_count = models.IntegerField(default=0)
    views_count = models.IntegerField(default=0)

    favorited_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='favorite_stores', blank=True)
    liked_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_stores', blank=True)
    followed_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='followed_stores', blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.store_name} ({self.user.email})"


class StoreComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=255)
    user_image = models.URLField(null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.user_name} on {self.store.store_name}"
