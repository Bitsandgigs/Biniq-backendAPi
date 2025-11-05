from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from .models import Product, ProductCategory
from .serializers import ProductSerializer, ProductCategorySerializer


class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        user = self.request.user
        qs = Product.objects.filter(user=user).select_related('category')
        type_param = self.request.query_params.get('type')
        if type_param:
            try:
                qs = qs.filter(type=int(type_param))
            except ValueError:
                pass
        return qs.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save()


class TrendingProductsView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Product.objects.filter(user=self.request.user, type=1)
            .select_related('category')
            .order_by('-created_at')[:50]
        )


class ActivityFeedView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Product.objects.filter(user=self.request.user, type=2)
            .select_related('category')
            .order_by('-created_at')[:50]
        )


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'product_id'
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user).select_related('category')


class CategoryListView(generics.ListAPIView):
    queryset = ProductCategory.objects.all().order_by('category_name')
    serializer_class = ProductCategorySerializer
    permission_classes = [AllowAny]


class CategoryCreateView(generics.CreateAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAuthenticated]


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = ProductCategory.objects.all().order_by('category_name')
    serializer_class = ProductCategorySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
