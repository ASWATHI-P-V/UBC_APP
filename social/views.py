from rest_framework import generics, permissions
from .models import SocialMediaLink, SocialMediaPlatform
from .serializers import SocialMediaLinkSerializer, SocialMediaPlatformSerializer
from accounts.utils import api_response
from rest_framework import status

from rest_framework.response import Response

class SocialMediaLinkListCreateView(generics.ListCreateAPIView):
    serializer_class = SocialMediaLinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.social_links.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            success=True,
            message="Social media links fetched successfully.",
            data=serializer.data
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return api_response(
            success=True,
            message="Social media link created successfully.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SocialMediaLinkDeleteView(generics.DestroyAPIView):
    serializer_class = SocialMediaLinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.social_links.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return api_response(
            success=True,
            message="Social media deleted successfully.",
            data=None
        )


class SocialMediaPlatformCreateView(generics.CreateAPIView):
    queryset = SocialMediaPlatform.objects.all()
    serializer_class = SocialMediaPlatformSerializer
    # permission_classes = [permissions.IsAdminUser]  # Optional: limit to admin

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return api_response(
            success=True,
            message="Social media platform created successfully.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED
        )
