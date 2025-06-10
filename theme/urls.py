from django.urls import path
from .views import ThemeRetrieveUpdateView

urlpatterns = [
    path('', ThemeRetrieveUpdateView.as_view(), name='theme-manage'),
]
