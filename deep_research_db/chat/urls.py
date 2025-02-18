# chat/urls.py
from django.urls import path
from . import api_views

urlpatterns = [
    path('save_chat/', api_views.save_chat, name='save_chat'),
]
