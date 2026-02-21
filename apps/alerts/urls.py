from django.urls import path
from . import views
urlpatterns = [
    path('', views.alert_list, name='alert_list'),
    path('<int:alert_id>/resolve/', views.resolve_alert, name='resolve_alert'),
    path('resolve-all/', views.resolve_all_alerts, name='resolve_all_alerts'),
]
