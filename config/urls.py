from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from apps.monitoring import views as monitoring_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('accounts/login/',  auth_views.LoginView.as_view(template_name='base/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/accounts/login/'), name='logout'),

    # Dashboard
    path('', monitoring_views.dashboard, name='dashboard'),

    # Device Monitor
    path('monitor/<int:device_id>/', monitoring_views.device_monitor, name='device_monitor'),
    path('monitoring/start-cycle/<int:device_id>/', monitoring_views.start_cycle, name='start_cycle'),
    path('monitoring/complete-cycle/<int:cycle_id>/', monitoring_views.complete_cycle, name='complete_cycle'),

    # Devices + PLC
    path('devices/', include('apps.devices.urls')),

    # Analytics
    path('energy/', include('apps.energy.urls')),
    path('costs/',  include('apps.costs.urls')),
    path('waste/',  include('apps.waste.urls')),

    # Operations
    path('alerts/', include('apps.alerts.urls')),
    path('reports/', include('apps.reports.urls')),

    # API
    path('api/v1/monitoring/', include('apps.monitoring.api_urls')),
    path('api/v1/devices/', include('apps.devices.api_urls')),
    path('api/v1/alerts/', include('apps.alerts.api_urls')),
]
