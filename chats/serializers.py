# messages/serializers.py
from rest_framework import serializers
from .models import Message # Import the Message model from the current app
from accounts.serializers import UserSerializer # Import UserSerializer from accounts app

class MessageListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing messages in a user's inbox.
    Includes full details of the sender.
    """
    sender_details = UserSerializer(source='sender', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'content', 'timestamp', 'is_read', 'sender_details']
        read_only_fields = ['sender', 'receiver', 'timestamp']

class MessageCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for sending a new message.
    Requires receiver ID and content. Sender is set automatically in the view.
    """
    class Meta:
        model = Message
        fields = ['id', 'receiver', 'content'] # 'sender' is set by the view, 'timestamp' is auto_now_add