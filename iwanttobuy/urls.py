from django.urls import path
from . import views

app_name = 'iwanttobuy'

urlpatterns = [
    # Main views
    path('', views.request_list, name='request_list'),
    path('create/', views.create_request, name='create_request'),
    path('<int:pk>/', views.request_detail, name='request_detail'),
    path('<int:pk>/edit/', views.edit_request, name='edit_request'),
    path('<int:pk>/delete/', views.delete_request, name='delete_request'),
    path('<int:pk>/fulfill/', views.mark_as_fulfilled, name='mark_as_fulfilled'),
    path('<int:pk>/respond/', views.respond_to_request, name='respond_to_request'),
    
    # User's requests and responses
    path('my-requests/', views.my_requests, name='my_requests'),
    path('my-responses/', views.my_responses, name='my_responses'),
]
