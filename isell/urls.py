from django.urls import path
from . import views

app_name = 'isell'

urlpatterns = [
    # Main views
    path('', views.item_list, name='item_list'),
    path('create/', views.create_item, name='create_item'),
    path('<int:pk>/', views.item_detail, name='item_detail'),
    path('<int:pk>/edit/', views.edit_item, name='edit_item'),
    path('<int:pk>/delete/', views.delete_item, name='delete_item'),
    path('<int:pk>/sold/', views.mark_as_sold, name='mark_as_sold'),
    
    # Saved items and messaging
    path('<int:pk>/save/', views.toggle_save_item, name='toggle_save_item'),
    path('<int:pk>/message/', views.send_message, name='send_message'),
    
    # User's items and messages
    path('my-items/', views.my_items, name='my_items'),
    path('saved-items/', views.saved_items, name='saved_items'),
    path('my-messages/', views.my_messages, name='my_messages'),
]
