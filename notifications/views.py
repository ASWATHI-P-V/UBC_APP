# notifications/views.py

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from django.shortcuts import get_object_or_404
from django.http import Http404 # For custom 404 response
from accounts.utils import api_response # Your custom api_response utility

from .models import Notification
from .serializers import NotificationSerializer, NotificationCreateSerializer
from rest_framework.response import Response

class NotificationListView(generics.ListAPIView):
    """
    API endpoint to list notifications for the logged-in user.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return notifications where the current authenticated user is the recipient.
        return Notification.objects.filter(recipient=self.request.user).order_by('-timestamp')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        if not queryset.exists():
            return api_response(False,"No notifications found.",None, status.HTTP_200_OK)
        
        serializer = self.get_serializer(queryset, many=True)
        return api_response(True,"Notifications retrieved successfully.",serializer.data, status.HTTP_200_OK)


class NotificationCreateView(generics.CreateAPIView): # <--- ADD THIS NEW VIEW
    """
    API endpoint for administrators to send notifications to users.
    Only accessible by authenticated admin users.
    """
    serializer_class = NotificationCreateSerializer
    # Only authenticated admin users can use this API
    permission_classes = [IsAuthenticated, IsAdminUser] 

    def perform_create(self, serializer):
        # Automatically set the sender of the notification to the authenticated admin user
        serializer.save(sender=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # DRF's CreateAPIView automatically generates a 'Location' header for 201 responses.
        headers = self.get_success_headers(serializer.data) 

        # Return the response using the standard DRF Response object for consistency with other create views
        return Response(
            data={
                "success": True,
                "message": "Notification sent successfully.",
                "data": serializer.data # Returns the created notification's data (fields from create serializer)
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class NotificationMarkAsReadView(generics.UpdateAPIView):
    """
    API endpoint to mark a specific notification as read.
    Only allows the recipient to mark their own notification as read.
    """
    queryset = Notification.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer # Use NotificationSerializer for consistent response format

    def get_object(self):
        # Retrieve the notification, ensuring it belongs to the current user as the recipient.
        return get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'], recipient=self.request.user)

    def update(self, request, *args, **kwargs):
        try:
            notification = self.get_object() # Attempt to get the notification
        except Http404:
            return api_response(False,"Notification not found or you do not have permission to mark it as read.",None, status.HTTP_400_BAD_REQUEST)

            

        if notification.is_read:
            return api_response(False,"Notification is already marked as read.",None, status.HTTP_400_BAD_REQUEST)

          
            
        notification.is_read = True 
        notification.save(update_fields=['is_read']) 
        serializer = self.get_serializer(notification)
        return api_response(True,"Notification marked as read.",serializer.data, status.HTTP_200_OK)

        