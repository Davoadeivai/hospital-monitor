from django.urls import path
from . import views
urlpatterns = [
    path('', views.waste_list, name='waste_list'),
]
