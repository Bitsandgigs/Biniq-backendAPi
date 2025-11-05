from django.urls import path
from .views import NotificationListCreateView, NotificationMarkReadView

urlpatterns = [
    path('', NotificationListCreateView.as_view(), name='notifications-list-create'),
    path('<uuid:notification_id>/read', NotificationMarkReadView.as_view(), name='notifications-mark-read'),
]
