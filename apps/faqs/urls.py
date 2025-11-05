from django.urls import path
from .views import FAQListCreateView, FAQDetailView

urlpatterns = [
    path('', FAQListCreateView.as_view(), name='faq-list-create'),
    path('<uuid:faq_id>', FAQDetailView.as_view(), name='faq-detail'),
]
