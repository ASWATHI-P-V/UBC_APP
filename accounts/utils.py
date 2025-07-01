import random
import phonenumbers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status

def _extract_single_error_message(errors_data):
    """
    Extracts a single, user-friendly error message from a DRF serializer's error dictionary.
    Prioritizes non-field errors, then the first error from the first field.
    """
    if isinstance(errors_data, dict):
        # Check for non_field_errors first
        if 'non_field_errors' in errors_data and errors_data['non_field_errors']:
            return str(errors_data['non_field_errors'][0])
        
        # Iterate through fields and return the first error message found
        for field, messages in errors_data.items():
            if isinstance(messages, list) and messages:
                return str(messages[0])
            elif isinstance(messages, dict): # Handle nested serializers or complex errors
                nested_message = _extract_single_error_message(messages)
                if nested_message:
                    return nested_message
    elif isinstance(errors_data, list) and errors_data:
        return str(errors_data[0])
        
    return "An unknown validation error occurred."


def api_response(success, message=None, data=None, status_code=status.HTTP_200_OK):
    """
    Generates a consistent API response.
    If it's a 400 Bad Request due to validation errors, it sets the 'message'
    to the specific error and sets 'data' to null.
    """
    response_data = {}
    response_data["success"] = success

    # Handle validation errors specifically for 400 status codes
    if not success and status_code == status.HTTP_400_BAD_REQUEST and isinstance(data, dict):
        # Extract a single, specific message for validation errors
        response_data["message"] = _extract_single_error_message(data)
        response_data["data"] = None # Set data to null for validation errors
    else:
        # For other errors or success responses, use provided message/data
        response_data["message"] = message if message is not None else ("Operation successful." if success else "An error occurred.")
        response_data["data"] = data

    return Response(response_data, status=status_code)

    
def generate_otp():
    return str(random.randint(1000, 9999))


def validate_phone_number(phone):
    if not phone.startswith('+'):
        raise ValidationError("Phone number must start with '+' and country code, e.g. +919876543210")
    try:
        phone_obj = phonenumbers.parse(phone, None)
    except phonenumbers.NumberParseException:
        raise ValidationError("Invalid phone number format")

    if not phonenumbers.is_valid_number(phone_obj):
        raise ValidationError("Invalid phone number")

    return phonenumbers.format_number(phone_obj, phonenumbers.PhoneNumberFormat.E164)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token) 
        
    }
