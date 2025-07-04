from django.urls import path
from .views import SocialMediaLinkListCreateView, SocialMediaLinkDeleteView, SocialMediaPlatformListCreateView, UserSocialMediaLinkDetailView,SocialMediaLinkRetrieveView

urlpatterns = [
    path('links/', SocialMediaLinkListCreateView.as_view(), name='socialmedia-link-list-create'),
    path('links/create/', SocialMediaLinkListCreateView.as_view(), name='socialmedia-link-create'),
    path('links/<int:pk>/', UserSocialMediaLinkDetailView.as_view(), name='socialmedia-link-update'),
    path('links/<int:pk>/', SocialMediaLinkRetrieveView.as_view(), name='socialmedia-link-detail'),
    path('platforms/create/', SocialMediaPlatformListCreateView.as_view(), name='platform-create'),
    path('platforms/', SocialMediaPlatformListCreateView.as_view(), name='platform-create'),
]
