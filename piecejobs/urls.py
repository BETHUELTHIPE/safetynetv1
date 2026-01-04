from django.urls import path
from . import views

app_name = 'business_services'

urlpatterns = [
    path('', views.job_list, name='service_list'),
    path('create/', views.create_job, name='create_service'),
    path('<int:pk>/', views.job_detail, name='service_detail'),
    path('<int:pk>/edit/', views.edit_job, name='edit_service'),
    path('<int:pk>/delete/', views.delete_job, name='delete_service'),
    path('<int:pk>/apply/', views.apply_job, name='apply_service'),
    path('<int:pk>/applications/', views.job_applications, name='service_applications'),
    path('my-services/', views.my_jobs, name='my_services'),
    path('my-applications/', views.my_applications, name='my_applications'),
]
