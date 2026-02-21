from django.urls import path
from . import views
urlpatterns = [
    path('', views.device_list, name='device_list'),
    path('<int:pk>/', views.device_detail, name='device_detail'),
    path('<int:device_id>/plc-config/', views.plc_config, name='plc_config'),
    path('<int:device_id>/plc-test/', views.plc_test, name='plc_test'),
    path('maintenance/', views.maintenance_log, name='maintenance_log_list'),
]
