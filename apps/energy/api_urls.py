from django.urls import path
from . import views
urlpatterns = [
    path('', views.energy_dashboard, name='api_energy'),
]
