from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from accounts.models import User,ProfileViewRecord
from .models import SavedContact
from .serializers import UserSerializer, SavedContactDetailSerializer, AddRemoveSavedContactSerializer, RecentlyViewedContactDetailSerializer
from accounts.utils import api_response

class SavedContactsListView(generics.ListAPIView):
    """
    API endpoint to list all users saved by the logged-in user.
    """
    serializer_class = SavedContactDetailSerializer # Use the serializer that includes saved_user_details
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return the SavedContact entries for the current authenticated user
        return SavedContact.objects.filter(user=self.request.user).select_related('saved_user')

    def list(self, request, *args, **kwargs):
        """
        Overrides the default list method to use the custom api_response structure.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # Use your custom api_response utility
        return api_response(True,"Saved contacts retrieved successfully.",serializer.data,status.HTTP_200_OK)


class AddRemoveSavedContactView(APIView):
    """
    API endpoint to add or remove another user as a contact.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = AddRemoveSavedContactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        target_user_id = serializer.validated_data['target_user_id']

        current_user = request.user

        if current_user.id == target_user_id:
            return api_response(False,"You cannot save yourself as a contact.", serializer.data)
        try:
            target_user = User.objects.get(id=target_user_id)
        except User.DoesNotExist:
            return api_response(False,"User to save not found.", serializer.data)
        # Check if the contact is already saved
        saved_contact_entry = SavedContact.objects.filter(user=current_user, saved_user=target_user).first()

        if saved_contact_entry:
            # If exists, remove it (unsave)
            saved_contact_entry.delete()
            return api_response(True, "Contact unsaved successfully.", serializer.data)
        else:
            # If not exists, create a new SavedContact entry (save)
            SavedContact.objects.create(user=current_user, saved_user=target_user)
            return api_response(True, "Contact saved successfully.", serializer.data)

class RecentlyViewedContactsListView(generics.ListAPIView):
    """
    API endpoint to list recently viewed contacts by the logged-in user.
    Ordered by the most recently viewed.
    """
    serializer_class = RecentlyViewedContactDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ProfileViewRecord.objects.filter(viewer=self.request.user).select_related('profile_owner').order_by('-viewed_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return api_response(True,"Recently viewed contacts retrieved successfully.",serializer.data,status.HTTP_200_OK)