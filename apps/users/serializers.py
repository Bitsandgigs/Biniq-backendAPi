from datetime import datetime
from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import User, Feedback
from apps.stores.models import Store


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password']


from rest_framework import serializers
from .models import User

class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'email', 'password',
            'role', 'store_name', 'phone_number', 'address'
        )
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 6}
        }

    def validate(self, attrs):
        role = attrs.get('role')

        # 🔹 Store Owner required fields
        if role == 3:
            if not attrs.get('store_name'):
                raise serializers.ValidationError({'store_name': 'Store name is required for Store Owner'})
            if not attrs.get('phone_number'):
                raise serializers.ValidationError({'phone_number': 'Mobile number is required for Store Owner'})
            if not attrs.get('address'):
                raise serializers.ValidationError({'address': 'Address is required for Store Owner'})

        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # hash password
        user.save()
        # Auto-create a Store for Store Owners to match Node.js behavior
        try:
            if user.role == 3:
                # Only create if one doesn't already exist (defensive)
                if not hasattr(user, 'store'):
                    Store.objects.create(
                        user=user,
                        store_name=user.store_name,
                        address=user.address,
                        phone_number=user.phone_number,
                        # Optionally tie store email to user email; comment out if undesired
                        store_email=user.email,
                    )
        except Exception:
            # Do not block registration if store creation fails; can be handled separately
            pass
        return user




class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        # Django's ModelBackend expects 'username' kwarg which maps to USERNAME_FIELD ('email').
        user = authenticate(request=self.context.get('request'), username=email, password=password)
        if not user:
            raise serializers.ValidationError('Invalid credentials')
        attrs['user'] = user
        return attrs


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'full_name', 'store_name', 'dob', 'gender', 'phone_number', 'address',
            'card_number', 'cardholder_name', 'expiry_month', 'expiry_year', 'cvc',
            'expertise_level', 'profile_image'
        )


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError({'old_password': 'Old password is incorrect'})
        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'user', 'rating', 'user_name', 'user_email', 'suggestion', 'type', 'status', 'reply', 'created_at']
        read_only_fields = ['id', 'user', 'user_name', 'user_email', 'type', 'status', 'reply', 'created_at']


class FeedbackCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['rating', 'suggestion']

    def create(self, validated_data):
        user = self.context['request'].user
        type_map = {2: 'reseller', 3: 'store_owner'}
        fb = Feedback.objects.create(
            user=user,
            rating=validated_data['rating'],
            user_name=user.full_name,
            user_email=user.email,
            suggestion=validated_data['suggestion'],
            type=type_map.get(user.role, 'store_owner'),
        )
        return fb


class FeedbackReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['reply']


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=6)
