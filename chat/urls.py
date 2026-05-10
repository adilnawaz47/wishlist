from django.urls import path
from . import views

urlpatterns = [
    path('', views.inbox, name='chat_inbox'),
    path('room/<int:room_id>/', views.room, name='chat_room'),
    path('start/<int:user_id>/', views.start_chat, name='start_chat'),
    path('room/<int:room_id>/send-image/', views.send_image, name='send_image'),
    path('unread/', views.unread_count, name='chat_unread'),
]
