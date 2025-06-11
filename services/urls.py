from django.urls import path
from .views import ServiceListCreateView,ServiceUpdateView, ServiceDeleteView

urlpatterns = [
    path('', ServiceListCreateView.as_view(), name='service-list-create'),
     path('<int:pk>/edit/', ServiceUpdateView.as_view(), name='service-edit'),
    path('<int:pk>/', ServiceDeleteView.as_view(), name='service-delete'),
   
]
