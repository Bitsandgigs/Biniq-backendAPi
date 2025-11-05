from django.urls import path
from .views import PromotionListCreateView, PromotionDetailView

urlpatterns = [
    path('AddPromotion', PromotionListCreateView.as_view(), name='promotion-list-create'),
    path('<uuid:promotion_id>', PromotionDetailView.as_view(), name='promotion-detail'),
]
