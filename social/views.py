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
            return api_response(False, "No social media links found for this user.", data=[])

        serializer = self.get_serializer(queryset, many=True)
        return api_response(True, "Social media links fetched successfully.", serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Custom create method with error handling for blank/invalid fields.
        """
        serializer = self.get_serializer(data=request.data)
        
        try:
            # Validate the serializer data. If validation fails, it will raise an exception.
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return api_response(
                True,
                "Social media link created successfully.",
                serializer.data,
                status.HTTP_201_CREATED
            )
        except serializers.ValidationError as e:
            # Catch validation errors and return them using your api_response format
            # e.detail contains a dictionary of validation errors for each field
            return api_response(
                False,
                "please provide the name, picture, and description.",
                [],
                status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # Catch any other unexpected errors during creation
            return api_response(
                False,
                f"An unexpected error occurred: {str(e)}",
                None,
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def perform_create(self, serializer):
        """
        Assigns the current user to the social media link before saving.
        """
        serializer.save(user=self.request.user)

    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     return api_response(True,"Social media link created successfully.",serializer.data,status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserSocialMediaLinkDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SocialMediaLinkSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Ensures users can only manage their own social media links.
        """
        return SocialMediaLink.objects.filter(user=self.request.user)


    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial, context={'request': request})

        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            return api_response(
                True,
                "Social media link updated successfully.",
                serializer.data,
                status.HTTP_200_OK
            )
        except serializers.ValidationError as e:
            return api_response(
                False,
                "Please provide valid data for social media link.",
                e.detail,
                status.HTTP_400_BAD_REQUEST
            )
        except NotFound:
            return api_response(
                success=False,
                message="Social media link not found or does not belong to the user.",
                data=None,
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return api_response(
                False,
                f"An unexpected error occurred: {str(e)}",
                None,
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SocialMediaLinkDeleteView(generics.DestroyAPIView):
    serializer_class = SocialMediaLinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Ensures that a user can only delete their own social media links.
        """
        return self.request.user.social_links.all()
    
    def destroy(self, request, *args, **kwargs):
        """
        Custom destroy method to return the ID of the deleted link in the response.
        """
        pk = kwargs.get('pk')
        print(f"[DEBUG] Attempting to delete SocialMediaLink ID: {pk}")
        print(f"[DEBUG] User's Links: {self.get_queryset().values_list('id', flat=True)}")

        # Get the instance before performing the destroy operation
        instance = self.get_object()
        deleted_id = instance.id # Store the ID before deletion

        # Perform the actual deletion
        self.perform_destroy(instance)
        
        # Return a success response with the ID of the deleted link in the 'data' part
        # Assuming api_response function signature is api_response(success, message, data)
        return api_response(True, "Social media link deleted successfully.", {'id': deleted_id})

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
        if not queryset.exists():
            return api_response(False, "No social media links found for this user.", data=[])
        
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
