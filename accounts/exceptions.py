# accounts/exceptions.py

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
# Import all necessary exception types from DRF
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, PermissionDenied, APIException, NotFound, ValidationError as DRFValidationError # Ensure NotFound and ValidationError are imported

# Import your api_response and _extract_single_error_message from your utils.py
# Assuming utils.py is directly in the 'accounts' app.
from .utils import api_response, _extract_single_error_message 

# --- IMPORT ALL YOUR SPECIFIC VIEW CLASSES FROM THEIR CORRECT APPS ---

# Import Service Views from the 'services' app
from services.views import ( 
    ServiceListCreateView, 
    ServiceRetrieveView, 
)

# Import Social Views from the 'social' app
from social.views import (
    SocialMediaLinkListCreateView, 
    UserSocialMediaLinkDetailView,
    SocialMediaLinkRetrieveView,
    SocialMediaPlatformListCreateView, # <-- Make sure this is also imported if you plan to use it
)
from theme.views import ( 
    ThemeRetrieveUpdateView, # <-- Make sure this is imported
)

# Import Theme Views from the 'themes' app (UNCOMMENT AND COMPLETE IF YOU HAVE THESE APPS/VIEWS)
# from themes.views import ( 
#     ThemeListView, 
#     ThemeRetrieveView,
# )

def custom_api_exception_handler(exc, context):
    response = exception_handler(exc, context) # Get DRF's default response first

    # If DRF's default handler produced a response (i.e., it was a DRF-related exception)
    if response is not None:
        view = context.get('view') # Get the view instance that caused the exception

        # --- Rule 1: Specific Authentication/Permission Errors per View Type ---

        # Case 1.1: Authentication/Permission for Service Views
        if isinstance(view, (ServiceListCreateView, ServiceRetrieveView)):
            if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
                # This specific rule for 'No service found for this user.'
                # when authentication fails for Service endpoints.
                return api_response(
                    success=True,
                    message="No service found for this user.",
                    data=[],
                    status_code=status.HTTP_200_OK
                )
            if isinstance(exc, NotFound):
                # Specific not found message for service
                return api_response(
                    success=False,
                    message="Service not found.",
                    data=None, # Or []
                    status_code=status.HTTP_404_NOT_FOUND
                )
            # Add more specific rules for Service views here (e.g., PermissionDenied)

        # Case 1.2: Authentication/Permission for Social Views
        # IMPORTANT: Make sure all social views are listed here
        elif isinstance(view, (SocialMediaLinkListCreateView, UserSocialMediaLinkDetailView,
                                SocialMediaLinkRetrieveView, SocialMediaPlatformListCreateView)): 
            if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
                # Differentiate response for list view vs. detail/single views on auth failure
                if isinstance(view, SocialMediaLinkListCreateView):
                     return api_response(
                        success=True, # You want success:true for the list when no data due to auth
                        message="No social media links found for this user.",
                        data=[],
                        status_code=status.HTTP_200_OK
                    )
                else: # For detail views (retrieve/update/delete) when auth fails
                    return api_response(
                        success=False,
                        message="Authentication required or social media link not found/accessible.",
                        data=None, # Or []
                        status_code=status.HTTP_401_UNAUTHORIZED # Or 404 depending on desired security info leakage
                    )
            if isinstance(exc, NotFound):
                return api_response(
                    success=False,
                    message="Social media link not found.",
                    data=None, # Or []
                    status_code=status.HTTP_404_NOT_FOUND
                )
            # Add more specific rules for Social views
        elif isinstance(view, ThemeRetrieveUpdateView): # <-- Use ThemeRetrieveUpdateView
            if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
                # THIS IS THE SPECIFIC CHANGE FOR THEME AUTHENTICATION FAILURE
                return api_response(
                    success=True,
                    message="User not found", # As explicitly requested for this scenario
                    data=[],
                    status_code=status.HTTP_200_OK
                )
            if isinstance(exc, NotFound):
                return api_response(
                    success=False,
                    message="Theme not found.", # Use 'Theme not found.' as a generic 404 for theme
                    data=None, 
                    status_code=status.HTTP_404_NOT_FOUND
                )
        # Case 1.3: Authentication/Permission for Theme Views (UNCOMMENT AND COMPLETE IF YOU HAVE THESE APPS/VIEWS)
        # elif isinstance(view, (ThemeListView, ThemeRetrieveView)):
        #     if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
        #         return api_response(
        #             success=False,
        #             message="Authentication required to access theme data.",
        #             data=None, # Or []
        #             status_code=status.HTTP_401_UNAUTHORIZED
        #         )
        #     if isinstance(exc, NotFound):
        #         return api_response(
        #             success=False,
        #             message="Theme not found.",
        #             data=None, # Or []
        #             status_code=status.HTTP_404_NOT_FOUND
        #         )
        # Add more specific rules for Theme views

        # --- Rule 2: Generic DRF Exception Handling (if not caught by specific view rules) ---
        # This acts as a fallback for any DRF exception not specifically handled above,
        # ensuring they still conform to your api_response structure.

        if isinstance(exc, DRFValidationError): # Handle ValidationErrors (e.g. from serializers)
            return api_response(
                success=False,
                message=_extract_single_error_message(response.data),
                data=None, # For validation errors, you set data to None
                status_code=status.HTTP_400_BAD_REQUEST
            )
        elif isinstance(exc, APIException): # Catch any other DRF APIException (e.g., ParseError, etc.)
            # For other APIExceptions, we default to success:false and use the DRF's 'detail' message
            message = response.data.get('detail', 'An API error occurred.') if isinstance(response.data, dict) else str(response.data)
            return api_response(
                success=False,
                message=message,
                data=response.data, # Include original data for debugging if not a 400 validation error
                status_code=response.status_code
            )

    # Fallback: If it's not a DRF exception, or no specific rule matched, return DRF's default response or None
    return response