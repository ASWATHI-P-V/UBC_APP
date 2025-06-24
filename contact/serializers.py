from rest_framework import serializers
from .models import SavedContact
from accounts.models import User,ProfileViewRecord
from accounts.serializers import UserSerializer

class SavedContactDetailSerializer(serializers.ModelSerializer):
    # This serializer is for returning the details of a saved contact entry.
    # It includes the full details of the saved_user.
    saved_user_details = UserSerializer(source='saved_user', read_only=True)

    class Meta:
        model = SavedContact
        fields = ['id', 'saved_user', 'saved_at', 'saved_user_details']
        read_only_fields = ['user', 'saved_at'] # User and saved_at are set automatically

class AddRemoveSavedContactSerializer(serializers.Serializer):
    # This serializer is for the POST request to add/remove a contact.
    target_user_id = serializers.IntegerField(help_text="The ID of the user to save/unsave.")


class RecentlyViewedContactDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying details of a recently viewed contact.
    It includes the full details of the profile_owner (the user who was viewed).
    """
    profile_owner_details = UserSerializer(source='profile_owner', read_only=True)

    class Meta:
        model = ProfileViewRecord
        fields = ['id', 'profile_owner', 'viewed_at', 'profile_owner_details']
        read_only_fields = ['viewer', 'viewed_at']
