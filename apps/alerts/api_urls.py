from django.urls import path
from . import views
urlpatterns = [
    path('resolve/<int:alert_id>/', views.resolve_alert),
]
