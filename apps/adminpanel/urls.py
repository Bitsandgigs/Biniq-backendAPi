from django.urls import path
from .views import (
    HealthView,
    ScansListView,
    ScanDetailView,
    ScanStatusView,
    ScanExportView,
    ScanAuditView,
    AnalyticsUserGrowthView,
    AnalyticsTrendsView,
    AnalyticsRevenueBreakdownView,
    AnalyticsSentimentView,
    AnalyticsGoalsView,
    TrendingView,
    LocationsListView,
    LocationsVerificationView,
    FeedbackStatsView,
    FeedbackSentimentView,
    ResellerPerformanceView,
    ResellerResourcesView,
    StoreContentView,
    StoreContentApproveView,
    StoreContentRollbackView,
    StoreAnalyticsView,
    PartnershipSubscriptionsView,
    AssignPartnershipPlanView,
)

urlpatterns = [
    path('health', HealthView.as_view(), name='api-health'),

    # Scans management
    path('scans', ScansListView.as_view(), name='scans-list'),
    path('scans/export', ScanExportView.as_view(), name='scans-export'),
    path('scans/<str:scan_id>', ScanDetailView.as_view(), name='scan-detail'),
    path('scans/<str:scan_id>/status', ScanStatusView.as_view(), name='scan-status'),
    path('scans/<str:scan_id>/audit', ScanAuditView.as_view(), name='scan-audit'),

    # Analytics
    path('analytics/user-growth', AnalyticsUserGrowthView.as_view(), name='analytics-user-growth'),
    path('analytics/trends', AnalyticsTrendsView.as_view(), name='analytics-trends'),
    path('analytics/revenue-breakdown', AnalyticsRevenueBreakdownView.as_view(), name='analytics-revenue-breakdown'),
    path('analytics/sentiment', AnalyticsSentimentView.as_view(), name='analytics-sentiment'),
    path('analytics/goals', AnalyticsGoalsView.as_view(), name='analytics-goals'),

    # Trending
    path('trending', TrendingView.as_view(), name='trending'),

    # Locations
    path('locations', LocationsListView.as_view(), name='locations'),
    path('locations/verification', LocationsVerificationView.as_view(), name='locations-verification'),

    # Feedback analytics
    path('feedback/stats', FeedbackStatsView.as_view(), name='feedback-stats'),
    path('feedback/sentiment', FeedbackSentimentView.as_view(), name='feedback-sentiment'),

    # Resellers
    path('resellers/<str:reseller_id>/performance', ResellerPerformanceView.as_view(), name='reseller-performance'),
    path('resellers/resources', ResellerResourcesView.as_view(), name='reseller-resources'),

    # Store content moderation and analytics
    path('stores/<str:store_id>/content', StoreContentView.as_view(), name='store-content'),
    path('stores/<str:store_id>/content/approve', StoreContentApproveView.as_view(), name='store-content-approve'),
    path('stores/<str:store_id>/content/rollback', StoreContentRollbackView.as_view(), name='store-content-rollback'),
    path('stores/<str:store_id>/analytics', StoreAnalyticsView.as_view(), name='store-analytics'),

    # Partnership Subscriptions
    path('partnership-subscriptions', PartnershipSubscriptionsView.as_view(), name='partnership-subscriptions'),
    path('partnership-subscriptions/assign', AssignPartnershipPlanView.as_view(), name='assign-partnership-plan'),
]
