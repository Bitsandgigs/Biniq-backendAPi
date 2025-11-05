from datetime import datetime
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from apps.products.models import ProductCategory
from apps.users.models import User
from .models import Promotion
from .serializers import PromotionSerializer


class PromotionListCreateView(generics.ListCreateAPIView):
    serializer_class = PromotionSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        user = self.request.user
        qs = Promotion.objects.filter(user=user).select_related('category')
        status_param = self.request.query_params.get('status')
        vis_param = self.request.query_params.get('visibility')
        if status_param:
            qs = qs.filter(status=status_param)
        if vis_param:
            qs = qs.filter(visibility=vis_param)
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        # Role check: store owners only (3)
        if user.role != 3:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Only store owners can create promotions')
        # Active subscription check
        if not user.subscription_end_time or timezone.now() > user.subscription_end_time:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('No active subscription')
        # Promotion limit check
        if user.used_promotions >= user.total_promotions:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Promotion limit reached')
        promo = serializer.save()
        # Update counters on user
        user.used_promotions = (user.used_promotions or 0) + 1
        user.save(update_fields=['used_promotions'])
        return promo


class PromotionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PromotionSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'promotion_id'
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return Promotion.objects.filter(user=self.request.user).select_related('category')

    def perform_destroy(self, instance):
        user = self.request.user
        super().perform_destroy(instance)
        if user.used_promotions and user.used_promotions > 0:
            user.used_promotions -= 1
            user.save(update_fields=['used_promotions'])
