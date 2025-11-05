from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Notification
from .serializers import NotificationSerializer


class NotificationListCreateView(generics.ListCreateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user).order_by('-created_at')
        read = self.request.query_params.get('read')
        if read is not None:
            if read.lower() == 'true':
                qs = qs.filter(read=True)
            elif read.lower() == 'false':
                qs = qs.filter(read=False)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, notification_id):
        notif = get_object_or_404(Notification, id=notification_id, user=request.user)
        notif.read = True
        notif.save(update_fields=['read'])
        return Response({'message': 'Notification marked as read'})
