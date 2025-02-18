# chat/urls.py
from django.urls import path
from . import api_views

urlpatterns = [
    path('save_chat/', api_views.save_chat, name='save_chat'),
    path('list/', api_views.list_chats, name='list_chats'),
    path('get/<int:session_id>/', api_views.get_chat, name='get_chat'),
]
