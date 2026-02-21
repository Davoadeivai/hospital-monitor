from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
    path('readings/<int:device_id>/', views.api_device_readings),
    path('resolve-alert/<int:alert_id>/', views.resolve_alert, name='api_resolve_alert'),
]
