from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from django.utils import timezone
from django.db.models import Sum, Count, Case, When, IntegerField
from django.db.models.functions import TruncMonth
from apps.users.models import Feedback, User
from apps.notifications.models import Notification
from .serializers import FeedbackSerializer, FeedbackCreateSerializer


class FeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Admin only: return all feedback
        if request.user.role != 1:
            return Response({'message': 'Only admins can view feedback'}, status=403)
        feedbacks = Feedback.objects.all().order_by('-created_at')
        data = FeedbackSerializer(feedbacks, many=True).data
        return Response(data)

    def post(self, request):
        # Reseller or Store Owner only: submit feedback
        if request.user.role == 1:
            return Response({'message': 'Admins cannot submit feedback'}, status=403)
        ser = FeedbackCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        fb = Feedback.objects.create(
            user=request.user,
            rating=ser.validated_data['rating'],
            user_name=request.user.full_name,
            user_email=request.user.email,
            suggestion=ser.validated_data['suggestion'],
            type='reseller' if request.user.role == 2 else 'store_owner',
            created_at=timezone.now(),
        )
        # Notify admin
        admin = User.objects.filter(role=1).first()
        if admin:
            Notification.objects.create(
                user=admin,
                heading='New Feedback Received',
                content=f"New feedback from {request.user.full_name} ({request.user.email}): Rating: {fb.rating}/5, Suggestion: {fb.suggestion}",
                type='reseller' if request.user.role == 2 else 'store_owner',
            )
            try:
                send_mail(
                    'New Feedback Received',
                    f"Feedback from {request.user.full_name} ({request.user.email}, {'reseller' if request.user.role == 2 else 'store_owner'}): Rating: {fb.rating}/5, Suggestion: {fb.suggestion}",
                    None,
                    [admin.email],
                    fail_silently=True,
                )
            except Exception:
                pass
        return Response({'message': 'Feedback submitted successfully'}, status=201)


class FeedbackReplyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Admin only
        if request.user.role != 1:
            return Response({'message': 'Only admins can reply to feedback'}, status=403)
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
        # Notify feedback user by email
        try:
            send_mail('Feedback Reply', f'Admin replied to your feedback: {reply}', None, [fb.user_email], fail_silently=True)
        except Exception:
            pass
        return Response({'message': 'Feedback replied successfully'})


class FeedbackSentimentTrendsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Admin only: aggregated monthly sentiment distribution (last 6 months)
        if request.user.role != 1:
            return Response({'message': 'Only admins can access this endpoint'}, status=403)

        now = timezone.now()
        start = now - timezone.timedelta(days=180)

        qs = (
            Feedback.objects.filter(created_at__gte=start)
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(
                total=Count('id'),
                positive=Sum(Case(When(rating__gte=4, then=1), default=0, output_field=IntegerField())),
                neutral=Sum(Case(When(rating=3, then=1), default=0, output_field=IntegerField())),
                negative=Sum(Case(When(rating__lte=2, then=1), default=0, output_field=IntegerField())),
            )
            .order_by('month')
        )

        def month_label(dt):
            return dt.strftime('%b') if hasattr(dt, 'strftime') else str(dt)

        data = []
        for row in qs:
            total = row['total'] or 0
            if total <= 0:
                pos_pct = neu_pct = neg_pct = 0
            else:
                pos_pct = round((row['positive'] or 0) * 100.0 / total, 2)
                neu_pct = round((row['neutral'] or 0) * 100.0 / total, 2)
                neg_pct = round((row['negative'] or 0) * 100.0 / total, 2)
            data.append({
                'month': month_label(row['month']),
                'positive': pos_pct,
                'neutral': neu_pct,
                'negative': neg_pct,
            })

        return Response({'success': True, 'data': data})
