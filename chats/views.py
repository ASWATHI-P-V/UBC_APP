# messages/views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404 # Needed for MessageMarkAsReadView

from accounts.models import User # Import User model from accounts app
from accounts.utils import api_response # Import your custom api_response utility

from .models import Message # Import Message model from current app
from .serializers import MessageListSerializer, MessageCreateSerializer # Import serializers from current app
from rest_framework.response import Response
from django.http import Http404

class MessageListView(generics.ListAPIView):
    """
    API endpoint to list messages delivered to the logged-in user (Inbox).
    """
    serializer_class = MessageListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return messages where the current authenticated user is the receiver.
        # Use select_related('sender') for efficient retrieval of sender details.
        # Order by timestamp in descending order (newest messages first).
        return Message.objects.filter(receiver=self.request.user).select_related('sender').order_by('-timestamp')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        return api_response(False,"No messages found for your inbox.",None, status.HTTP_200_OK)

        serializer = self.get_serializer(queryset, many=True)

class MessageCreateView(generics.CreateAPIView):
    """
    API endpoint to send a new message to another user.
    """
    serializer_class = MessageCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Automatically set the sender of the message to the current authenticated user.
        serializer.save(sender=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer) # Call perform_create to save the message
        headers = self.get_success_headers(serializer.data)
        
        return Response(
            data={
                "success": True,
                "message": "Message sent successfully.",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )
        

class MessageMarkAsReadView(generics.UpdateAPIView):
    """
    API endpoint to mark a specific message as read.
    Only allows the receiver of the message to mark it as read.
    """
    queryset = Message.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = MessageListSerializer # Use MessageListSerializer for consistent response format

    def get_object(self):
        # Retrieve the message, ensuring it belongs to the current user as the receiver.
        # This prevents users from marking other people's messages as read.
        return get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'], receiver=self.request.user)


    def update(self, request, *args, **kwargs):
        try:
            # Attempt to retrieve the message. If not found, Http404 is raised.
            message = self.get_object() 
        except Http404:
            # Catch the Http404 exception and return your custom response
            return api_response(False,"Message not found or you do not have permission to mark it as read.",None,status.HTTP_404_NOT_FOUND)

        # If the message was found (i.e., Http404 was not raised), proceed with original logic
        if message.is_read:
            return api_response(False,"Message is already marked as read.",None,status.HTTP_400_BAD_REQUEST)
        
        message.is_read = True 
        message.save(update_fields=['is_read']) 
        serializer = self.get_serializer(message)
        return api_response(True,"Message marked as read.",serializer.data,status.HTTP_200_OK)
    # def update(self, request, *args, **kwargs):
    #     message = self.get_object()
    #     if message.is_read:
    #         return api_response(False,"Message is already marked as read.",status.HTTP_400_BAD_REQUEST)
    #     message.is_read = True # Set is_read to True
    #     message.save(update_fields=['is_read']) # Only update the is_read field in the database
    #     serializer = self.get_serializer(message)
    #     return api_response(True,"Message marked as read.",serializer.data,status.HTTP_200_OK)