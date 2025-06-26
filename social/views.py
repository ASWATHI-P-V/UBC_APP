from rest_framework import generics, permissions
from .models import SocialMediaLink, SocialMediaPlatform
from .serializers import SocialMediaLinkSerializer, SocialMediaPlatformSerializer
from accounts.utils import api_response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

class SocialMediaLinkListCreateView(generics.ListCreateAPIView):
    serializer_class = SocialMediaLinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.social_links.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return api_response(False, "No social media links found for this user.", data=None)

        serializer = self.get_serializer(queryset, many=True)
        return api_response(True, "Social media links fetched successfully.", serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return api_response(True,"Social media link created successfully.",serializer.data,status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SocialMediaLinkDeleteView(generics.DestroyAPIView):
    serializer_class = SocialMediaLinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.social_links.all()
    
    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        print("[DEBUG] Deleting SocialMediaLink ID:", pk)
        print("[DEBUG] User's Links:", self.get_queryset().values_list('id', flat=True))

        instance = self.get_object()
        self.perform_destroy(instance)
        return api_response(True, "Social media deleted successfully.", None)


    # def destroy(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     self.perform_destroy(instance)
    #     return api_response(True,"Social media deleted successfully.",None)


class SocialMediaPlatformListCreateView(generics.ListCreateAPIView):
    queryset = SocialMediaPlatform.objects.all()
    serializer_class = SocialMediaPlatformSerializer
    # permission_classes = [permissions.IsAdminUser]  # Optional

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return api_response(True, "Social media platforms fetched successfully.", serializer.data, status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            return api_response(False, "Social media platform with this name already exists.", None, status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        return api_response(True, "Social media platform created successfully.", serializer.data, status.HTTP_201_CREATED)
