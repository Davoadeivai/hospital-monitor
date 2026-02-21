from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('monitor/<int:device_id>/', views.device_monitor, name='device_monitor'),
    path('monitoring/start-cycle/<int:device_id>/', views.start_cycle, name='start_cycle'),
    path('monitoring/complete-cycle/<int:cycle_id>/', views.complete_cycle, name='complete_cycle'),
    path('api/readings/<int:device_id>/', views.api_device_readings, name='api_device_readings'),
]
