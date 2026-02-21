from django.urls import path
from . import views

urlpatterns = [
    path('', views.device_list, name='api_device_list'),
]
