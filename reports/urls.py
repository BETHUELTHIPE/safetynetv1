from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('submit/', views.submit_report, name='submit_report'),
    path('list/', views.reports, name='report_list'), # Existing reports view, renamed for clarity
    path('<int:pk>/detail/', views.report_detail, name='report_detail'), # New: Detail view for a single report
    path('map-data/', views.crime_map_data, name='crime_map_data'), # New: API endpoint for map data
    path('map/', views.crime_map_view, name='crime_map'), # New: Crime Map view
]
