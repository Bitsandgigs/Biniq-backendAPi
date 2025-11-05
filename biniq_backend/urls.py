"""
URL configuration for biniq_backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('apps.users.urls')),
    path('api/products/', include('apps.products.urls')),
    path('api/categories/', include('apps.products.urls_categories')),
    path('api/stores/', include('apps.stores.urls')),
    path('api/subscriptions/', include('apps.subscriptions.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/faqs/', include('apps.faqs.urls')),
    path('api/promotions/', include('apps.promotions.urls')),
    path('api/stats/', include('apps.stats.urls')),
    path('api/', include('apps.adminpanel.urls')),
    path('api/feedback/', include('apps.feedback.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
