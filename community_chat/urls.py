from django.urls import path
from . import views

app_name = 'community_chat'

urlpatterns = [
    path('', views.chatboard, name='chatboard'),
    path('post/', views.post_message, name='post_message'),
    path('message/<int:message_id>/delete/', views.delete_message, name='delete_message'),
    path('message/<int:message_id>/react/', views.toggle_reaction, name='toggle_reaction'),
    path('api/messages/', views.get_messages, name='get_messages'),
]
