from django.urls import path
from .views import FeedbackView, FeedbackReplyView, FeedbackSentimentTrendsView

urlpatterns = [
    path('', FeedbackView.as_view(), name='feedback-list-create'),
    path('reply', FeedbackReplyView.as_view(), name='feedback-reply'),
    path('sentiment-trends', FeedbackSentimentTrendsView.as_view(), name='feedback-sentiment-trends'),
]
