"""
URL configuration for cpfcrimereportingsystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('reports/', include('reports.urls')),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('report-crime/', views.crime_reporting_dashboard, name='crime_reporting_dashboard'),
    # Temporarily disabled due to issues
    # path('community-dashboard/', include('dashboard.urls')),
    
    # Use the accounts app for authentication
    path('accounts/', include('accounts.urls')),
    
    # Other app includes
    path('analytics/', include('analytics.urls')),
    path('chat/', include('community_chat.urls')),
    path('events/', include('kingspark_events.urls')),
    path('business-services/', include('piecejobs.urls', namespace='business_services')),
    path('isell/', include('isell.urls', namespace='isell')),
    path('iwanttobuy/', include('iwanttobuy.urls', namespace='iwanttobuy')),
    path('services/', include('services.urls', namespace='services')),
    path('alerts/', include('community_alerts.urls', namespace='community_alerts')),
    
    # Static pages
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('terms/', views.terms_and_conditions, name='terms_and_conditions'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('safety-tips/', views.safety_tips, name='safety_tips'),
    path('emergency-contacts/', views.emergency_contacts, name='emergency_contacts'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
