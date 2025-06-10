from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Theme
from .serializers import ThemeSerializer
from accounts.utils import api_response

def api_response(success, message, data=None, status_code=status.HTTP_200_OK):
    return Response({
        "success": success,
        "message": message,
        "data": data
    }, status=status_code)

class ThemeRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = ThemeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Get or create a theme only for the logged-in user
        theme, created = Theme.objects.get_or_create(user=self.request.user)
        return theme

    def get(self, request, *args, **kwargs):
        theme = self.get_object()
        serializer = self.get_serializer(theme)
        return api_response(True, "Theme fetched successfully", serializer.data)

    def put(self, request, *args, **kwargs):
        theme = self.get_object()
        serializer = self.get_serializer(theme, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return api_response(True, "Theme updated successfully", serializer.data)

    