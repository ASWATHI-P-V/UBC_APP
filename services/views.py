from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Service
from .serializers import ServiceSerializer
from accounts.utils import api_response
from rest_framework.exceptions import NotFound
from rest_framework import serializers # Import serializers for ValidationError

class ServiceListCreateView(generics.ListCreateAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.services.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return api_response(True, "No service found for this user.", data=[], status_code=status.HTTP_200_OK) 

        serializer = self.get_serializer(queryset, many=True)
        return api_response(True, "Service fetched successfully.", serializer.data, status_code=status.HTTP_200_OK) # Added status_code


    

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            return api_response(
                success=False,
                message=" Please provide all necessary details.",
                data=[], # e.detail will contain the validation errors
                status_code=status.HTTP_400_BAD_REQUEST
            )
        self.perform_create(serializer)
        return api_response(
            success=True,
            message="Service created successfully.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ServiceRetrieveView(generics.RetrieveAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Ensures that a user can only retrieve their own services.
        Admins might see all, if a separate permission handles that.
        """
        # Assuming `Service` model has a ForeignKey to User, and User has related_name='services'
        return self.request.user.services.all()

    def retrieve(self, request, *args, **kwargs):
        """
        Custom retrieve method to use api_response for consistent output.
        """
        try:
            instance = self.get_object() # get_object() automatically applies get_queryset filter
        except NotFound:
            return api_response(
                success=False,
                message="Service not found or does not belong to the user.",
                data=None,
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(instance)
        return api_response(
            success=True,
            message="Service retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )



class ServiceUpdateView(generics.UpdateAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only allow the current user's services
        return self.request.user.services.all()

    def get_object(self):
        try:
            return super().get_object()
        except NotFound:
            # Handle "not found" explicitly
            raise NotFound(detail="Service not found or does not belong to the user.")

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except NotFound as e:
            return api_response(
                success=False,
                message=str(e),
                data=None,
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            return api_response(
                success=False,
                message="Validation failed. Please check the provided details.",
                data=e.detail,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        self.perform_update(serializer)

        return api_response(
            success=True,
            message="Service updated successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    def perform_update(self, serializer):
        serializer.save()

        
class ServiceDeleteView(generics.DestroyAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Ensures that a user can only delete their own services.
        """
        return self.request.user.services.all()

    def delete(self, request, *args, **kwargs):
        """
        Custom delete method to return the ID of the deleted service in the response's data part.
        """
        try:
            # Get the instance of the service to be deleted
            instance = self.get_object()
        except NotFound:
            return api_response(
                success=False,
                message="Service not found or does not belong to the user.",
                data=None,
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        # Store the ID before the service is actually deleted
        deleted_id = instance.id

        # Perform the actual deletion
        self.perform_destroy(instance)
        
        # Return a success response with the ID of the deleted service in the 'data' part.
        # Changed status_code from HTTP_204_NO_CONTENT to HTTP_200_OK because we are
        # returning content (the deleted ID) in the response body.
        return api_response(
            success=True,
            message=f"Service with ID {deleted_id} deleted successfully.",
            data={'id': deleted_id},
            status_code=status.HTTP_200_OK
        )

# class ServiceDeleteView(generics.DestroyAPIView):
#     serializer_class = ServiceSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         return self.request.user.services.all()

#     def delete(self, request, *args, **kwargs):
#         instance = self.get_object()
#         self.perform_destroy(instance)
#         return api_response(
#             success=True,
#             message="Service deleted successfully.",
#             data=None,
#             status_code=status.HTTP_204_NO_CONTENT
#         )

# Assuming Service model and api_response utility are defined elsewhere.
# For completeness, here's a placeholder for api_response and Service model if not provided:

