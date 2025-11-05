from datetime import datetime
from django.db.models import Count, Sum
from django.utils import timezone
from django.core.mail import send_mail
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.users.models import User
from apps.notifications.models import Notification
from .models import Plan, Subscription
from .serializers import PlanSerializer, SubscriptionSerializer, SubscriptionCreateSerializer


PROMOTION_LIMITS = {'tier1': 20, 'tier2': 50, 'tier3': 100}
SCAN_LIMITS = {'tier1': 20, 'tier2': 50, 'tier3': 100}


def generate_order_id():
    year = timezone.now().year
    prefix = f"ORD-{year}-"
    latest = Subscription.objects.filter(order_id__startswith=prefix).order_by('-order_id').first()
    seq = 1
    if latest:
        try:
            seq = int(latest.order_id.split('-')[2]) + 1
        except Exception:
            seq = 1
    return f"{prefix}{str(seq).zfill(3)}"


class SubscriptionTiersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role not in (1, 2):
            return Response({'success': False, 'message': 'Only admins and resellers can access this endpoint'}, status=403)
        query = {} if user.role == 1 else {'type': 'reseller'}
        plans = Plan.objects.filter(**query)
        data = {'reseller': {}, 'store_owner': {}}
        for p in plans:
            data[p.type][p.tier] = {'plan_id': str(p.id), 'amount': float(p.amount), 'duration': p.duration}
        if user.role == 2:
            data.pop('store_owner', None)
        return Response({'success': True, 'data': data})

    def put(self, request):
        # admin only
        if request.user.role != 1:
            return Response({'success': False, 'message': 'Only admins can update tiers'}, status=403)
        tiers = request.data.get('tiers', [])
        if not isinstance(tiers, list):
            return Response({'success': False, 'message': 'Tiers must be an array'}, status=400)
        for t in tiers:
            if t.get('type') not in ('reseller', 'store_owner'):
                return Response({'success': False, 'message': 'Invalid type'}, status=400)
            if t.get('tier') not in ('tier1', 'tier2', 'tier3'):
                return Response({'success': False, 'message': 'Invalid tier'}, status=400)
            amount = t.get('amount')
            duration = t.get('duration')
            if amount is None or float(amount) < 0:
                return Response({'success': False, 'message': 'Amount must be non-negative'}, status=400)
            if duration is None or int(duration) < 1:
                return Response({'success': False, 'message': 'Duration must be positive'}, status=400)
            Plan.objects.update_or_create(type=t['type'], tier=t['tier'], defaults={'amount': amount, 'duration': duration})
        updated = Plan.objects.all()
        data = {'reseller': {}, 'store_owner': {}}
        for p in updated:
            data[p.type][p.tier] = {'amount': float(p.amount), 'duration': p.duration}
        return Response({'success': True, 'message': 'Subscription tiers updated successfully', 'data': data})


class AllSubscriptionsAdminView(generics.ListAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role != 1:
            self.permission_denied(self.request, message='Only admins can access this endpoint')
        return Subscription.objects.filter(status='completed').select_related('user')


class ManageSubscriptionCountsView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        if request.user.role != 1:
            return Response({'success': False, 'message': 'Only admins can manage subscription counts'}, status=403)
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'success': False, 'message': 'User ID is required'}, status=400)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'success': False, 'message': 'User not found'}, status=404)
        if user.role == 1:
            return Response({'success': False, 'message': 'Cannot manage counts for admins'}, status=403)
        sub = None
        if user.subscription:
            sub = Subscription.objects.filter(id=user.subscription, status='completed').first()
        if not sub:
            if user.role == 3:
                user.total_promotions = 0
            elif user.role == 2:
                user.total_scans = 0
            user.save()
            return Response({'success': True, 'message': 'Counts reset due to no active subscription', 'data': {
                'user_id': str(user.id), 'total_promotions': user.total_promotions, 'used_promotions': user.used_promotions or 0, 'total_scans': user.total_scans
            }})
        limits = SCAN_LIMITS if user.role == 2 else PROMOTION_LIMITS
        limit_val = limits.get(sub.plan, 0)
        if user.role == 3:
            user.total_promotions = limit_val
        else:
            user.total_scans = limit_val
        user.save()
        Notification.objects.create(user=user, heading='Subscription Limits Updated', content=f"Your {'promotion' if user.role==3 else 'scan'} limit has been updated to {limit_val} based on your {sub.plan} subscription.", type='store_owner' if user.role==3 else 'reseller')
        try:
            send_mail('Subscription Limits Updated', f"Your {'promotion' if user.role==3 else 'scan'} limit has been updated to {limit_val}.", None, [user.email], fail_silently=True)
        except Exception:
            pass
        return Response({'success': True, 'message': 'Subscription counts updated successfully', 'data': {
            'user_id': str(user.id), 'total_promotions': user.total_promotions or 0, 'used_promotions': user.used_promotions or 0, 'total_scans': user.total_scans or 0
        }})


class SubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SubscriptionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        plan_tier = serializer.validated_data['plan']
        user = request.user
        if user.role == 1:
            return Response({'message': 'Admins cannot subscribe'}, status=403)
        type_val = 'reseller' if user.role == 2 else 'store_owner'
        try:
            plan_cfg = Plan.objects.get(type=type_val, tier=plan_tier)
        except Plan.DoesNotExist:
            return Response({'message': 'Invalid plan for user type'}, status=400)
        order_id = generate_order_id()
        pm = serializer.validated_data['payment_method']
        sub = Subscription.objects.create(
            order_id=order_id,
            user=user,
            user_name=user.full_name,
            type=type_val,
            plan=plan_tier,
            amount=plan_cfg.amount,
            status='completed',
            duration=plan_cfg.duration,
            date=timezone.now(),
            card_number=pm['card_number'],
            cardholder_name=pm['cardholder_name'],
            expiry_month=pm['expiry_month'],
            expiry_year=pm['expiry_year'],
            cvc=pm['cvc'],
        )
        # Update user subscription data
        user.subscription = sub.id
        user.subscription_end_time = timezone.now() + timezone.timedelta(days=sub.duration)
        if user.role == 3:
            user.total_promotions = PROMOTION_LIMITS.get(plan_tier, 0)
            user.used_promotions = 0
        elif user.role == 2:
            user.total_scans = SCAN_LIMITS.get(plan_tier, 0)
        user.save()
        Notification.objects.create(user=user, heading='Subscription Successful', content=f"Subscribed to {plan_tier} plan successfully. Subscription ends on {user.subscription_end_time.date()}. Your {'promotion' if user.role==3 else 'scan'} limit is {user.total_promotions if user.role==3 else user.total_scans}.", type=type_val)
        try:
            send_mail('Subscription Confirmation', f"You have subscribed to the {plan_tier} plan.", None, [user.email], fail_silently=True)
        except Exception:
            pass
        data = SubscriptionSerializer(sub).data
        return Response({'message': f'Subscribed to {plan_tier} plan successfully', 'subscription': data})


class UserSubscriptionsView(generics.ListAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user).order_by('-date')


class CancelSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.role == 1:
            return Response({'message': 'Admins cannot cancel subscriptions'}, status=403)
        if not user.subscription:
            return Response({'message': 'No active subscription'}, status=400)
        sub = Subscription.objects.filter(id=user.subscription).first()
        if not sub:
            return Response({'message': 'Subscription not found'}, status=404)
        sub.status = 'failed'
        sub.save(update_fields=['status'])
        user.subscription = None
        user.subscription_end_time = None
        if user.role == 3:
            user.total_promotions = 0
        elif user.role == 2:
            user.total_scans = 0
        user.save()
        type_val = 'reseller' if user.role == 2 else 'store_owner'
        Notification.objects.create(user=user, heading='Subscription Cancelled', content='Your subscription has been cancelled. Your promotion/scan limit has been reset to 0.', type=type_val)
        try:
            send_mail('Subscription Cancelled', 'Your subscription has been cancelled.', None, [user.email], fail_silently=True)
        except Exception:
            pass
        return Response({'message': 'Subscription cancelled successfully'})
