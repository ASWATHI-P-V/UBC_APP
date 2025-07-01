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

    
    # def list(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()

    #     if not queryset.exists():
    #         return api_response(False, "No theme found for this user.", data=None)

    #     serializer = self.get_serializer(queryset, many=True)
    #     return api_response(True, "Themes fetched successfully.", serializer.data)


    def get(self, request, *args, **kwargs):
        theme = self.get_object()
        # If the theme does not exist, it will be created by get_object
        if not theme:   
            return api_response(False, "Theme not found for this user.", [])
        serializer = self.get_serializer(theme)
        return api_response(True, "Theme fetched successfully", serializer.data)

    def put(self, request, *args, **kwargs):
        theme = self.get_object()
        serializer = self.get_serializer(theme, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return api_response(True, "Theme updated successfully", serializer.data)

    