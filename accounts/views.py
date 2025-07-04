from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User,ProfileViewRecord
from .utils import generate_otp, get_tokens_for_user
from django.utils import timezone
from .serializers import UserSerializer, UserProfileUpdateSerializer,UserListSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework import permissions
from phonenumbers import parse, is_valid_number, format_number, PhoneNumberFormat, NumberParseException
from django.core.cache import cache
from rest_framework import status
from accounts.utils import api_response
from phonenumbers import parse, is_valid_number, format_number, NumberParseException, PhoneNumberFormat
from django.contrib.auth import get_user_model

def api_response(success, message, data=None, status_code=status.HTTP_200_OK):
    return Response({
        "success": success,
        "message": message,
        "data": data
    }, status=status_code)


# Request OTP for Login
class RequestPhoneOTP(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data, partial=True)  # partial=True to only validate mobile_number
        if not serializer.is_valid():
            return api_response(False, "Validation error", data=serializer.errors, status_code=400)

        mobile_number = serializer.validated_data.get("mobile_number")

        user = User.objects.filter(mobile_number=mobile_number).first()
        if not user:
            return api_response(False, "User does not exist. Please sign up first.", status_code=404)

        otp = generate_otp()
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()

        print(f"[DEBUG] OTP for {mobile_number}: {otp}")
        return api_response(True, "OTP sent sucesssfully to mobile number", data={"otp": otp})


# Verify Login OTP
class VerifyPhoneOTP(APIView):
    def post(self, request):
        otp_input = request.data.get("otp")

        serializer = UserSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return api_response(False, "Validation error", data=serializer.errors, status_code=400)

        mobile_number = serializer.validated_data.get("mobile_number")

        user = User.objects.filter(mobile_number=mobile_number, otp=otp_input).first()
        if user and user.is_otp_valid(otp_input):
            user.otp = None
            user.otp_created_at = None
            user.save()
            tokens = get_tokens_for_user(user)
            user_data = UserSerializer(user).data
            return api_response(True, "Login successful", data={
                "access": tokens["access"],
                #"token": tokens["refresh"],
                "user": user_data
            })

        return api_response(False, "Invalid or expired OTP", status_code=400)



class SignupRequest(APIView):
    def post(self, request):
        data = request.data

        raw_mobile = data.get("mobile_number")
        country_code = data.get("country_code")
        email = data.get("email")

        # Validate presence of mobile and country code
        if not raw_mobile or not country_code:
            return api_response(False, "Mobile number and country code are required", data=None, status_code=400)

        # Normalize the mobile number to E.164 format
        try:
            # If number starts with +, trust it and try parsing
            if raw_mobile.startswith("+"):
                parsed = parse(raw_mobile, None)
            else:
                parsed = parse(f"{country_code}{raw_mobile}", None)

            if not is_valid_number(parsed):
                return api_response(False, "Invalid mobile number", data=None, status_code=400)

            normalized_mobile = format_number(parsed, PhoneNumberFormat.E164)
            normalized_country_code = f"+{parsed.country_code}"

        except NumberParseException as e:
            return api_response(False, f"Mobile number parse error: {str(e)}", data=None, status_code=400)

        # Check for duplicate mobile/email BEFORE serializer.is_valid()
        if User.objects.filter(mobile_number=normalized_mobile).exists():
            return api_response(False, "Mobile number already registered", data=None, status_code=400)

        if email and User.objects.filter(email=email).exists():
            return api_response(False, "Email already registered", data=None, status_code=400)

        # Inject the normalized values back into request data
        data["mobile_number"] = normalized_mobile
        data["country_code"] = normalized_country_code

        serializer = UserSerializer(data=data)
        if not serializer.is_valid():
            return api_response(False, "Validation error", data=serializer.errors, status_code=400)

        try:
            validated = serializer.validated_data
            mobile_number = validated.get('mobile_number')  # E.164 format

            otp = generate_otp()
            cache_key = f"signup_otp:{mobile_number}"
            print(f"[DEBUG] SignupRequest cache key: {cache_key}, otp: {otp}")

            cache.set(cache_key, {
                "otp": otp,
                "signup_data": validated,
                "created_at": timezone.now().isoformat()
            }, timeout=300)  # 5 minutes

            return api_response(True, "OTP sent for verification", data={"otp": otp})

        except Exception as e:
            print(f"[ERROR] SignupRequest failed: {str(e)}")
            return api_response(False, "Internal server error", data=None, status_code=500)




class FinalizeSignup(APIView):
    def post(self, request):
        otp_input = request.data.get("otp")
        mobile_number_raw = request.data.get("mobile_number")
        country_code = request.data.get("country_code")

        if not mobile_number_raw or not country_code:
            return api_response(False, "Mobile number and country code are required.", status_code=400)

        # Normalize to E.164 format
        try:
            parsed = parse(f"{country_code}{mobile_number_raw}", None)
            if not is_valid_number(parsed):
                return api_response(False, "Invalid mobile number", status_code=400)
            mobile_number = format_number(parsed, PhoneNumberFormat.E164)
        except NumberParseException as e:
            return api_response(False, f"Number parse error: {str(e)}", status_code=400)

        # Now get from cache using normalized number
        cache_key = f"signup_otp:{mobile_number}"
        otp_data = cache.get(cache_key)

        print(f"[DEBUG] FinalizeSignup cache key: {cache_key}, value: {otp_data}")

        if not otp_data:
            return api_response(False, "OTP expired or not found", status_code=400)

        if otp_input != otp_data["otp"]:
            return api_response(False, "Invalid OTP", status_code=400)

        otp_created = timezone.datetime.fromisoformat(otp_data["created_at"])
        if (timezone.now() - otp_created).total_seconds() > 300:
            return api_response(False, "OTP expired", status_code=400)

        serializer = UserSerializer(data=otp_data["signup_data"])
        if not serializer.is_valid():
            return api_response(False, "Signup data invalid", data=serializer.errors, status_code=400)

        user = User.objects.create(**serializer.validated_data)

        # Clear the OTP after success
        cache.delete(cache_key)

        tokens = get_tokens_for_user(user)
        user_data = UserSerializer(user).data

        return api_response(True, "User registered successfully", data={
            "access": tokens["access"],
            "user": user_data
        })



# Profile Update View
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserProfileUpdateSerializer(user)
        return api_response(
            success=True,
            message="Profile fetched successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    def put(self, request):
        user = request.user
        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return api_response(
                True,
                "Profile updated successfully",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        else:
            error_message = "Validation Error" # Default generic message
            if serializer.errors:
                first_field = next(iter(serializer.errors))
                if serializer.errors[first_field] and isinstance(serializer.errors[first_field], list):
                    error_message = serializer.errors[first_field][0]
                elif 'non_field_errors' in serializer.errors and serializer.errors['non_field_errors']:
                    error_message = serializer.errors['non_field_errors'][0]

            return api_response(
                False,
                error_message,
                data=None, # <--- CHANGED THIS LINE to pass None for data
                status_code=status.HTTP_400_BAD_REQUEST
            )

        

class ProfileDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]  # Or allow any if public

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        if request.user.is_authenticated and request.user != instance:
            # Check if the view is unique
            profile_view_record, created = ProfileViewRecord.objects.update_or_create(
                viewer=request.user,
                profile_owner=instance,
                defaults={'viewed_at': timezone.now()} # Always update the timestamp to now
            )
            if created: # This 'created' variable comes from update_or_create above
                instance.profile_views = (instance.profile_views or 0) + 1
                instance.save(update_fields=["profile_views"])
            # if not already_viewed:
            #     # Create a record and increment unique view count
            #     ProfileViewRecord.objects.create(profile_owner=instance, viewer=request.user)
            #     instance.profile_views = (instance.profile_views or 0) + 1
            #     instance.save(update_fields=["profile_views"])

        serializer = self.get_serializer(instance)
        return api_response(
            success=True,
            message="Profile fetched successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )


User = get_user_model()

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer # Use the serializer for listing users
    permission_classes = [permissions.IsAuthenticated] # Only authenticated users can view the list

    # Override the list method to use your custom api_response helper
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            success=True,
            message="List of all registered users fetched successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )


User = get_user_model()

class ProfilePublicDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = [] # <--- ADD THIS LINE!

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # The view counting logic should still check if the request is from an authenticated user
        # to ensure only logged-in users contribute to unique views.
        if request.user.is_authenticated and request.user != instance:
            profile_view_record, created = ProfileViewRecord.objects.update_or_create(
                viewer=request.user,
                profile_owner=instance,
                defaults={'viewed_at': timezone.now()}
            )
            if created:
                instance.profile_views = (instance.profile_views or 0) + 1
                instance.save(update_fields=["profile_views"])

        serializer = self.get_serializer(instance)
        return api_response(
            success=True,
            message="Profile fetched successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )



