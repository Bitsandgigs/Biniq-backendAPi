from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from apps.users.models import User
from .models import FAQ
from .serializers import FAQSerializer


class FAQListCreateView(generics.ListCreateAPIView):
    serializer_class = FAQSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 2:
            return FAQ.objects.filter(type=2).order_by('-created_at')
        elif user.role == 1:
            return FAQ.objects.all().order_by('-created_at')
        else:
            return FAQ.objects.filter(type=3).order_by('-created_at')

    def perform_create(self, serializer):
        # Admin only
        if self.request.user.role != 1:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Only admins can create FAQs')
        serializer.save()


class FAQDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FAQSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'faq_id'

    def get_queryset(self):
        return FAQ.objects.all()

    def perform_update(self, serializer):
        if self.request.user.role != 1:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Only admins can update FAQs')
        serializer.save()

    def delete(self, request, *args, **kwargs):
        if request.user.role != 1:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Only admins can delete FAQs')
        return super().delete(request, *args, **kwargs)
