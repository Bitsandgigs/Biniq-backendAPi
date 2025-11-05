from django.urls import path
from .views import (
    PaidUsersView,
    StoreOwnersView,
    ResellersView,
    RevenueView,
    RecentActivityView,
    RecentFeedbacksView,
    QuickStatsView,
)

urlpatterns = [
    path('paid-users', PaidUsersView.as_view(), name='stats-paid-users'),
    path('store-owners', StoreOwnersView.as_view(), name='stats-store-owners'),
    path('resellers', ResellersView.as_view(), name='stats-resellers'),
    path('revenue', RevenueView.as_view(), name='stats-revenue'),
    path('recent-activity', RecentActivityView.as_view(), name='stats-recent-activity'),
    path('recent-feedbacks', RecentFeedbacksView.as_view(), name='stats-recent-feedbacks'),
    path('quick-stats', QuickStatsView.as_view(), name='stats-quick-stats'),
]
