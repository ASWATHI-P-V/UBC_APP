from django.urls import path
from .views import ServiceListCreateView, ServiceDeleteView

urlpatterns = [
    path('', ServiceListCreateView.as_view(), name='service-list-create'),
    path('<int:pk>/', ServiceDeleteView.as_view(), name='service-delete'),
]
