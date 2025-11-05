from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.core.mail import send_mail
import random
from .models import User, Feedback
from apps.stores.models import Store
from apps.notifications.models import Notification
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    UpdateProfileSerializer,
    ChangePasswordSerializer,
    FeedbackSerializer,
)



class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]



class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        data = {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        }
        return Response(data)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        serializer = UpdateProfileSerializer(instance=request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password changed successfully"})


class FeedbackListCreateView(generics.ListCreateAPIView):
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Admins can see all feedback; others see their own
        if user.role == 1:
            return Feedback.objects.select_related('user').all().order_by('-created_at')
        return Feedback.objects.filter(user=user).order_by('-created_at')

    def perform_create(self, serializer):
        from .serializers import FeedbackCreateSerializer
        create_serializer = FeedbackCreateSerializer(data=self.request.data, context={'request': self.request})
        create_serializer.is_valid(raise_exception=True)
        create_serializer.save()


class FeedbackReplyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Admin only
        if request.user.role != 1:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Only admins can reply to feedback')
        feedback_id = request.data.get('feedback_id')
        reply = request.data.get('reply')
        if not feedback_id or not reply:
            return Response({'message': 'feedback_id and reply are required'}, status=400)
        fb = Feedback.objects.filter(id=feedback_id).first()
        if not fb:
            return Response({'message': 'Feedback not found'}, status=404)
        fb.reply = reply
        fb.status = 'replied'
        fb.save(update_fields=['reply', 'status'])
        return Response({'message': 'Reply added successfully'})


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        from .serializers import ForgotPasswordSerializer
        ser = ForgotPasswordSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email = ser.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=404)
        otp = f"{random.randint(100000, 999999)}"
        user.reset_password_token = otp
        user.reset_password_expires = timezone.now() + timezone.timedelta(minutes=10)
        user.save(update_fields=['reset_password_token', 'reset_password_expires'])
        try:
            send_mail('Password Reset OTP', f'Your OTP for password reset is: {otp}', None, [email], fail_silently=True)
        except Exception:
            pass
        return Response({'message': 'OTP sent to email'})


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        from .serializers import VerifyOTPSerializer
        ser = VerifyOTPSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email = ser.validated_data['email']
        otp = ser.validated_data['otp']
        try:
            user = User.objects.get(email=email, reset_password_token=otp)
        except User.DoesNotExist:
            return Response({'message': 'Invalid or expired OTP'}, status=400)
        if not user.reset_password_expires or user.reset_password_expires < timezone.now():
            return Response({'message': 'Invalid or expired OTP'}, status=400)
        return Response({'message': 'OTP verified successfully'})


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        from .serializers import ResetPasswordSerializer
        ser = ResetPasswordSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email = ser.validated_data['email']
        otp = ser.validated_data['otp']
        new_password = ser.validated_data['new_password']
        try:
            user = User.objects.get(email=email, reset_password_token=otp)
        except User.DoesNotExist:
            return Response({'message': 'Invalid or expired OTP'}, status=400)
        if not user.reset_password_expires or user.reset_password_expires < timezone.now():
            return Response({'message': 'Invalid or expired OTP'}, status=400)
        user.set_password(new_password)
        user.reset_password_token = None
        user.reset_password_expires = None
        user.save(update_fields=['password', 'reset_password_token', 'reset_password_expires'])
        return Response({'message': 'Password reset successfully'})


class AdminUserDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        # Admin only
        if request.user.role != 1:
            return Response({'success': False, 'message': 'Only admins can access user details'}, status=403)
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({'success': False, 'message': 'User not found'}, status=404)
        if user.role == 1:
            return Response({'success': False, 'message': 'Cannot fetch details of admin users'}, status=403)

        store = None
        if user.role == 3:
            store_obj = Store.objects.filter(user=user).first()
            if not store_obj:
                return Response({'success': False, 'message': 'Store not found for store owner'}, status=404)
            store = {
                '_id': str(store_obj.id),
                'store_name': store_obj.store_name,
                'user_latitude': store_obj.user_latitude,
                'user_longitude': store_obj.user_longitude,
                'address': store_obj.address,
                'favorited_by': list(store_obj.favorited_by.values_list('id', flat=True)),
                'liked_by': list(store_obj.liked_by.values_list('id', flat=True)),
                'followed_by': list(store_obj.followed_by.values_list('id', flat=True)),
                'comments': [{'user_name': c.user_name, 'content': c.content, 'created_at': c.created_at} for c in store_obj.comments.all()],
            }

        data = {
            'success': True,
            'data': {
                'user': {
                    '_id': str(user.id),
                    'full_name': user.full_name,
                    'store_name': user.store_name or None,
                    'email': user.email,
                    'role': 'reseller' if user.role == 2 else 'store_owner',
                    'dob': user.dob,
                    'gender': user.gender,
                    'phone_number': user.phone_number,
                    'address': user.address,
                    'expertise_level': user.expertise_level,
                    'profile_image': user.profile_image.url if getattr(user.profile_image, 'url', None) else user.profile_image if isinstance(user.profile_image, str) else None,
                    'subscription': user.subscription,
                    'subscription_end_time': user.subscription_end_time,
                    'total_promotions': user.total_promotions,
                    'used_promotions': user.used_promotions,
                    'promotions': [],
                    'verified': user.verified,
                    'total_scans': user.total_scans,
                    'scans_used': [],
                    'created_at': user.created_at,
                    'updated_at': user.updated_at,
                },
                'store': store,
            }
        }
        return Response(data)


class AdminAllStoreOwnersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 1:
            return Response({'success': False, 'message': 'Only admins can access all users details'}, status=403)
        users = User.objects.filter(role=3)
        result = []
        for u in users:
            store_obj = Store.objects.filter(user=u).first()
            store = None
            if store_obj:
                store = {
                    '_id': str(store_obj.id),
                    'store_name': store_obj.store_name,
                    'user_latitude': store_obj.user_latitude,
                    'user_longitude': store_obj.user_longitude,
                    'address': store_obj.address,
                    'favorited_by': list(store_obj.favorited_by.values_list('id', flat=True)),
                    'liked_by': list(store_obj.liked_by.values_list('id', flat=True)),
                    'followed_by': list(store_obj.followed_by.values_list('id', flat=True)),
                    'comments': [{'user_name': c.user_name, 'content': c.content, 'created_at': c.created_at} for c in store_obj.comments.all()],
                }
            result.append({
                'user': {
                    '_id': str(u.id),
                    'full_name': u.full_name,
                    'store_name': u.store_name or None,
                    'email': u.email,
                    'role': 'store_owner',
                    'dob': u.dob,
                    'gender': u.gender,
                    'phone_number': u.phone_number,
                    'address': u.address,
                    'expertise_level': u.expertise_level,
                    'profile_image': u.profile_image.url if getattr(u.profile_image, 'url', None) else u.profile_image if isinstance(u.profile_image, str) else None,
                    'subscription': u.subscription,
                    'subscription_end_time': u.subscription_end_time,
                    'total_promotions': u.total_promotions,
                    'used_promotions': u.used_promotions,
                    'promotions': [],
                    'verified': u.verified,
                    'total_scans': u.total_scans,
                    'scans_used': [],
                    'created_at': u.created_at,
                    'updated_at': u.updated_at,
                },
                'store': store,
            })
        return Response({'success': True, 'data': result})


class AdminAllResellersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 1:
            return Response({'success': False, 'message': 'Only admins can access all users details'}, status=403)
        users = User.objects.filter(role=2)
        result = []
        for u in users:
            result.append({
                'user': {
                    '_id': str(u.id),
                    'full_name': u.full_name,
                    'store_name': u.store_name or None,
                    'email': u.email,
                    'role': 'reseller',
                    'dob': u.dob,
                    'gender': u.gender,
                    'phone_number': u.phone_number,
                    'address': u.address,
                    'expertise_level': u.expertise_level,
                    'profile_image': u.profile_image.url if getattr(u.profile_image, 'url', None) else u.profile_image if isinstance(u.profile_image, str) else None,
                    'subscription': u.subscription,
                    'subscription_end_time': u.subscription_end_time,
                    'total_promotions': u.total_promotions,
                    'used_promotions': u.used_promotions,
                    'promotions': [],
                    'verified': u.verified,
                    'total_scans': u.total_scans,
                    'scans_used': [],
                    'created_at': u.created_at,
                    'updated_at': u.updated_at,
                }
            })
        return Response({'success': True, 'data': result})


class ApproveStoreOwnerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'message': 'User ID is required'}, status=400)
        if request.user.role != 1:
            return Response({'message': 'Only admins can approve store owners'}, status=403)
        user = User.objects.filter(id=user_id, role=3).first()
        if not user:
            return Response({'message': 'User not found'}, status=404)
        user.verified = True
        user.save(update_fields=['verified'])
        Notification.objects.create(user=user, heading='Account Verified', content='Your store owner account has been verified.', type='store_owner')
        try:
            send_mail('Account Verified', 'Your store owner account has been verified.', None, [user.email], fail_silently=True)
        except Exception:
            pass
        return Response({'message': 'Store owner approved successfully'})


class RejectStoreOwnerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'message': 'User ID is required'}, status=400)
        if request.user.role != 1:
            return Response({'message': 'Only admins can reject store owners'}, status=403)
        user = User.objects.filter(id=user_id, role=3).first()
        if not user:
            return Response({'message': 'User not found'}, status=404)
        user.verified = False
        user.save(update_fields=['verified'])
        Notification.objects.create(user=user, heading='Account Rejected', content='Your store owner account has been rejected.', type='store_owner')
        try:
            send_mail('Account Rejected', 'Your store owner account has been rejected.', None, [user.email], fail_silently=True)
        except Exception:
            pass
        return Response({'message': 'Store owner rejected successfully'})


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'message': 'User ID is required for admin deletion'}, status=400)
        if request.user.role != 1:
            return Response({'message': 'Only admins can delete accounts'}, status=403)
        user_to_delete = User.objects.filter(id=user_id).first()
        if not user_to_delete:
            return Response({'message': 'User to delete not found'}, status=404)
        # Also delete linked store if exists
        Store.objects.filter(user=user_to_delete).delete()
        user_to_delete.delete()
        return Response({'message': 'Account deleted successfully'})
