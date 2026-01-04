from django.urls import path
from . import views

app_name = 'community_alerts'

urlpatterns = [
    path('', views.alert_list, name='alert_list'),
    path('<int:pk>/', views.alert_detail, name='alert_detail'),
    path('create/', views.create_alert, name='create_alert'),
    path('<int:pk>/edit/', views.edit_alert, name='edit_alert'),
    path('<int:pk>/approve/', views.approve_alert, name='approve_alert'),
    path('<int:pk>/send/', views.send_alert, name='send_alert'),
    path('api/unread-count/', views.unread_alerts_count, name='unread_alerts_count'),
]
