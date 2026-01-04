from django.urls import path
from . import views_minimal as views

app_name = 'dashboard'

urlpatterns = [
    path('', views.community_dashboard, name='community_dashboard'),
]
