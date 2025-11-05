from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Sum, Avg
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.users.models import User, Feedback
from apps.subscriptions.models import Subscription


class PaidUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 1:
            return Response({'success': False, 'message': 'Only admins can access this endpoint'}, status=403)
        total_paid = Subscription.objects.filter(status='completed').count()
        last_month_cutoff = timezone.now() - timedelta(days=30)
        last_month_paid = Subscription.objects.filter(status='completed', date__lte=last_month_cutoff).count()
        increase = 0.0
        if last_month_paid > 0:
            increase = ((total_paid - last_month_paid) / last_month_paid) * 100.0
        return Response({'success': True, 'data': {'totalPaidUsers': total_paid, 'monthlyIncreasePercentage': round(increase, 2)}})


class StoreOwnersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 1:
            return Response({'success': False, 'message': 'Only admins can access this endpoint'}, status=403)
        total = User.objects.filter(role=3).count()
        last_month_cutoff = timezone.now() - timedelta(days=30)
        last_month_total = User.objects.filter(role=3, created_at__lte=last_month_cutoff).count()
        increase = 0.0
        if last_month_total > 0:
            increase = ((total - last_month_total) / last_month_total) * 100.0
        return Response({'success': True, 'data': {'totalStoreOwners': total, 'monthlyIncreasePercentage': round(increase, 2)}})


class ResellersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 1:
            return Response({'success': False, 'message': 'Only admins can access this endpoint'}, status=403)
        total = User.objects.filter(role=2).count()
        last_month_cutoff = timezone.now() - timedelta(days=30)
        last_month_total = User.objects.filter(role=2, created_at__lte=last_month_cutoff).count()
        increase = 0.0
        if last_month_total > 0:
            increase = ((total - last_month_total) / last_month_total) * 100.0
        return Response({'success': True, 'data': {'totalResellers': total, 'monthlyIncreasePercentage': round(increase, 2)}})


class RevenueView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 1:
            return Response({'success': False, 'message': 'Only admins can access this endpoint'}, status=403)
        total_revenue = Subscription.objects.filter(status='completed').aggregate(total=Sum('amount')).get('total') or 0
        last_month_cutoff = timezone.now() - timedelta(days=30)
        last_month_revenue = Subscription.objects.filter(status='completed', date__lte=last_month_cutoff).aggregate(total=Sum('amount')).get('total') or 0
        increase = 0.0
        if last_month_revenue > 0:
            increase = ((float(total_revenue) - float(last_month_revenue)) / float(last_month_revenue)) * 100.0
        return Response({'success': True, 'data': {'totalRevenue': float(total_revenue), 'monthlyIncreasePercentage': round(increase, 2)}})


class RecentActivityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 1:
            return Response({'success': False, 'message': 'Only admins can access this endpoint'}, status=403)
        last_24 = timezone.now() - timedelta(hours=24)
        users = User.objects.filter(created_at__gte=last_24, role__in=[2,3]).values('full_name', 'role', 'created_at')
        data = []
        for u in users:
            hours = (timezone.now() - u['created_at']).total_seconds() / 3600.0
            data.append({'name': u['full_name'], 'type': 'reseller' if u['role']==2 else 'store_owner', 'timeInHours': int(hours)})
        return Response({'success': True, 'data': data})


class RecentFeedbacksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 1:
            return Response({'success': False, 'message': 'Only admins can access this endpoint'}, status=403)
        last_24 = timezone.now() - timedelta(hours=24)
        feedbacks = Feedback.objects.filter(created_at__gte=last_24).values('rating', 'user_name', 'user_email', 'suggestion', 'type', 'status', 'reply', 'created_at')
        return Response({'success': True, 'data': list(feedbacks)})


class QuickStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 1:
            return Response({'success': False, 'message': 'Only admins can access this endpoint'}, status=403)
        total_users = User.objects.filter(role__in=[2,3]).count()
        premium_users = Subscription.objects.filter(status='completed').values('user').distinct().count()
        premium_pct = round((premium_users / total_users) * 100.0, 2) if total_users > 0 else 0.0
        avg_rating = Feedback.objects.aggregate(avg=Avg('rating')).get('avg') or 0
        pending_replies = Feedback.objects.filter(status='pending').count()
        active_subs = Subscription.objects.filter(status='completed').count()
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        new_users_today = User.objects.filter(role__in=[2,3], created_at__gte=today_start).count()
        return Response({'success': True, 'data': {
            'premiumUsers': {'count': premium_users, 'percentage': premium_pct},
            'averageRating': round(float(avg_rating), 1) if avg_rating else 0.0,
            'pendingReplies': pending_replies,
            'activeSubscriptions': active_subs,
            'newUsersToday': new_users_today,
        }})
