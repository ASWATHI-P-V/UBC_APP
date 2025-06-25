# notifications/urls.py

from django.urls import path
from .views import (
    NotificationListView,
    NotificationCreateView,
    NotificationMarkAsReadView
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('send/', NotificationCreateView.as_view(), name='notification-send'),
    path('mark-read/<int:pk>/', NotificationMarkAsReadView.as_view(), name='notification-mark-read'),
]