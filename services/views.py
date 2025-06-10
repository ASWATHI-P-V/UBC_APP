from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Service
from .serializers import ServiceSerializer
from accounts.utils import api_response

class ServiceListCreateView(generics.ListCreateAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.services.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            success=True,
            message="Service list fetched successfully.",
            data=serializer.data
        )

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
