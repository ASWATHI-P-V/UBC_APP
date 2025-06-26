from django.urls import path
from .views import SocialMediaLinkListCreateView, SocialMediaLinkDeleteView, SocialMediaPlatformListCreateView

urlpatterns = [
    path('links/', SocialMediaLinkListCreateView.as_view(), name='socialmedia-link-list-create'),
    path('links/<int:pk>/', SocialMediaLinkDeleteView.as_view(), name='socialmedia-link-delete'),
    path('platforms/create/', SocialMediaPlatformListCreateView.as_view(), name='platform-create'),
    path('platforms/', SocialMediaPlatformListCreateView.as_view(), name='platform-create'),
]
