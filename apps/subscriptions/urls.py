from django.urls import path
from .views import (
    SubscriptionTiersView,
    AllSubscriptionsAdminView,
    ManageSubscriptionCountsView,
    SubscribeView,
    UserSubscriptionsView,
    CancelSubscriptionView,
)

urlpatterns = [
    path('tiers', SubscriptionTiersView.as_view(), name='subscription-tiers'),
    path('all', AllSubscriptionsAdminView.as_view(), name='subscription-all'),
    path('manage-counts', ManageSubscriptionCountsView.as_view(), name='subscription-manage-counts'),
    path('subscribe', SubscribeView.as_view(), name='subscription-subscribe'),
    path('', UserSubscriptionsView.as_view(), name='subscription-list'),
    path('cancel', CancelSubscriptionView.as_view(), name='subscription-cancel'),
]
