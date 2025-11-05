import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            # set unusable; registration should always set password though
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 1)  # Admin
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        (1, 'Admin'),
        (2, 'Reseller'),
        (3, 'Store Owner'),
    )
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    EXPERTISE_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('expert', 'Expert'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # 🔹 Figma fields
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=255, blank=True)

    store_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES)

    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    phone_number = models.CharField(max_length=30, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    card_number = models.CharField(max_length=32, null=True, blank=True)
    cardholder_name = models.CharField(max_length=255, null=True, blank=True)
    expiry_month = models.CharField(max_length=2, null=True, blank=True)
    expiry_year = models.CharField(max_length=4, null=True, blank=True)
    cvc = models.CharField(max_length=4, null=True, blank=True)

    expertise_level = models.CharField(max_length=20, choices=EXPERTISE_CHOICES, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)

    subscription = models.UUIDField(null=True, blank=True)
    subscription_end_time = models.DateTimeField(null=True, blank=True)

    total_promotions = models.IntegerField(default=0)
    used_promotions = models.IntegerField(default=0)

    verified = models.BooleanField(default=False)
    total_scans = models.IntegerField(default=0)

    # Password reset (OTP)
    reset_password_token = models.CharField(max_length=6, null=True, blank=True)
    reset_password_expires = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']

    objects = UserManager()

    def save(self, *args, **kwargs):
        # Auto-generate full_name
        self.full_name = f"{self.first_name} {self.last_name}".strip()
        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.email



class Feedback(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('replied', 'Replied'),
    )
    TYPE_CHOICES = (
        ('reseller', 'Reseller'),
        ('store_owner', 'Store Owner'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    rating = models.PositiveSmallIntegerField()
    user_name = models.CharField(max_length=255)
    user_email = models.EmailField()
    suggestion = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reply = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Feedback from {self.user_email}: {self.suggestion[:20]}"
