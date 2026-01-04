from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('category-distribution/', views.crime_category_distribution, name='category_distribution'),
    path('trends-monthly/', views.crime_trends_monthly, name='trends_monthly'),
    path('trends-daily/', views.crime_trends_daily, name='trends_daily'),
    path('', views.analytics_dashboard_view, name='dashboard'),
]
