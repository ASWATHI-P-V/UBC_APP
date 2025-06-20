from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Service
from .serializers import ServiceSerializer
from accounts.utils import api_response
from rest_framework.exceptions import NotFound

class ServiceListCreateView(generics.ListCreateAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.services.all()

    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return api_response(False, "No service found for this user.", data=None)

        serializer = self.get_serializer(queryset, many=True)
        return api_response(True, "Service fetched successfully.", serializer.data)


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return api_response(
            success=True,
            message="Service created successfully.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



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
        serializer.is_valid(raise_exception=True)
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
        return self.request.user.services.all()

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return api_response(
            success=True,
            message="Service deleted successfully.",
            data=None,
            status_code=status.HTTP_204_NO_CONTENT
        )
