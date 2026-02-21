from django.urls import path
from . import views
urlpatterns = [
    path('', views.costs_dashboard, name='costs_dashboard'),
]
