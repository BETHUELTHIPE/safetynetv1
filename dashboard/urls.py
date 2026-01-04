from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('community/', views.community_dashboard, name='community_dashboard'),
]
