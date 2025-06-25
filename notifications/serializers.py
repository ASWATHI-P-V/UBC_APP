# notifications/serializers.py

from rest_framework import serializers
from .models import Notification
from accounts.serializers import UserSerializer # Assuming you have a UserSerializer

class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for listing notifications.
    Includes sender details if a sender is present.
    """
    sender_details = UserSerializer(source='sender', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'sender', 'sender_details', 'title', 'message', 
            'timestamp', 'is_read', 'link', 'notification_type'
        ]
        read_only_fields = ['recipient', 'sender', 'timestamp'] # Recipient/sender set by view/admin


    
class NotificationCreateSerializer(serializers.ModelSerializer): # <--- ADD THIS NEW SERIALIZER
    """
    Serializer for admin to create new notifications.
    Requires recipient ID, title, message, and optionally link and notification_type.
    Sender is set automatically to the authenticated admin user.
    """
    class Meta:
        model = Notification
        fields = ['recipient', 'title', 'message', 'link', 'notification_type']
        # 'sender', 'timestamp', and 'is_read' are handled by the view or model defaults.
