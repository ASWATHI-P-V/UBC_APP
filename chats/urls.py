# messages/urls.py
from django.urls import path
from .views import (
    MessageListView,
    MessageCreateView,
    MessageMarkAsReadView
)

urlpatterns = [
    path('', MessageListView.as_view(), name='message-inbox'), # e.g., /api/messages/
    path('send/', MessageCreateView.as_view(), name='message-send'), # e.g., /api/messages/send/
    path('mark-read/<int:pk>/', MessageMarkAsReadView.as_view(), name='message-mark-read'), # e.g., /api/messages/123/mark-read/
]