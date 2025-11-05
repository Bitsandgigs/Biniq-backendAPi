from django.urls import path
from .views import (
    ProductListCreateView,
    TrendingProductsView,
    ActivityFeedView,
    ProductDetailView,
    CategoryListCreateView,
)

urlpatterns = [
    path('products', ProductListCreateView.as_view(), name='product-list-create'),
    path('trending', TrendingProductsView.as_view(), name='product-trending'),
    path('activity', ActivityFeedView.as_view(), name='product-activity'),
    path('<uuid:product_id>', ProductDetailView.as_view(), name='product-detail'),
    path('AddCategory', CategoryListCreateView.as_view(), name='category-list-create'),
]


