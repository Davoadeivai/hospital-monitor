from django.urls import path
from . import views
urlpatterns = [
    path('', views.energy_dashboard, name='energy_dashboard'),
    path('tariffs/', views.tariff_list, name='tariff_list'),
]
