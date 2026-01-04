from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    # Main views
    path('', views.service_list, name='service_list'),
    path('create/', views.create_service, name='create_service'),
    path('<int:pk>/', views.service_detail, name='service_detail'),
    path('<int:pk>/edit/', views.edit_service, name='edit_service'),
    path('<int:pk>/delete/', views.delete_service, name='delete_service'),
    path('<int:pk>/pause/', views.pause_service, name='pause_service'),
    path('<int:pk>/activate/', views.activate_service, name='activate_service'),
    path('<int:pk>/review/', views.add_review, name='add_review'),
    path('<int:pk>/inquiry/', views.send_inquiry, name='send_inquiry'),
    path('<int:pk>/mark-read/', views.mark_inquiry_read, name='mark_inquiry_read'),
    
    # Categories
    path('category/<int:category_id>/', views.category_services, name='category_services'),
    
    # User's services, reviews, and inquiries
    path('my-services/', views.my_services, name='my_services'),
    path('my-reviews/', views.my_reviews, name='my_reviews'),
    path('my-inquiries/', views.my_inquiries, name='my_inquiries'),
]
