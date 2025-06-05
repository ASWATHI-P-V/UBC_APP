from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .utils import generate_otp, get_tokens_for_user
from django.utils import timezone
from .serializers import UserSerializer, UserProfileUpdateSerializer
from rest_framework.permissions import IsAuthenticated


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
        return api_response(True, "OTP sent to mobile number", data={"otp": otp})


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


# Collect Signup Data and Send OTP
class SignupRequest(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            return api_response(False, "Validation error", data=serializer.errors, status_code=400)

        data = serializer.validated_data
        mobile_number = data.get('mobile_number')
        email = data.get('email')

        if User.objects.filter(mobile_number=mobile_number).exists():
            return api_response(False, "Mobile number already registered", status_code=400)

        if email and User.objects.filter(email=email).exists():
            return api_response(False, "Email already registered", status_code=400)

        otp = generate_otp()

        request.session["signup_data"] = data
        request.session["signup_otp"] = otp
        request.session["signup_otp_time"] = timezone.now().isoformat()

        print(f"[DEBUG] Signup OTP for {mobile_number}: {otp}")
        return api_response(True, "OTP sent for verification", data={"otp": otp})


# Finalize Signup
class FinalizeSignup(APIView):
    def post(self, request):
        otp_input = request.data.get("otp")
        signup_data = request.session.get("signup_data")
        otp_sent = request.session.get("signup_otp")
        otp_time_str = request.session.get("signup_otp_time")

        if not signup_data or not otp_sent or not otp_time_str:
            return api_response(False, "Signup session expired or invalid", status_code=400)

        if otp_input != otp_sent:
            return api_response(False, "Invalid OTP", status_code=400)

        otp_created = timezone.datetime.fromisoformat(otp_time_str)
        if (timezone.now() - otp_created).total_seconds() > 300:
            return api_response(False, "OTP expired", status_code=400)

        serializer = UserSerializer(data=signup_data)
        if not serializer.is_valid():
            return api_response(False, "Signup data invalid", data=serializer.errors, status_code=400)

        user = User.objects.create(**serializer.validated_data)

        for key in ["signup_data", "signup_otp", "signup_otp_time"]:
            request.session.pop(key, None)

        tokens = get_tokens_for_user(user)
        user_data = UserSerializer(user).data

        print(f"[DEBUG] User created: {user.mobile_number} - {user.name or 'Unregistered'}")

        return api_response(True, "User registered successfully", data={
            "access": tokens["access"],
            #"token": tokens["refresh"],
            "user": user_data
        })


# Profile Update View
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
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

        return api_response(
            False,
            "Validation error",
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
        
        
# # views.py

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .models import User
# from .utils import generate_otp
# from django.utils import timezone
# from .serializers import UserSerializer,UserProfileUpdateSerializer
# from .utils import get_tokens_for_user
# from rest_framework.permissions import IsAuthenticated



# def api_response(success, message, data=None, status_code=status.HTTP_200_OK):
#     return Response({
#         "success": success,
#         "message": message,
#         "data": data
#     }, status=status_code)


# # Request OTP for Login
# class RequestPhoneOTP(APIView):
#     def post(self, request):
#         serializer = UserSerializer(data=request.data, partial=True)  # partial=True to only validate phone
#         if not serializer.is_valid():
#             return api_response(False, "Validation error", data=serializer.errors, status_code=400)

#         phone = serializer.validated_data.get("phone")

#         user = User.objects.filter(phone=phone).first()
#         if not user:
#             return api_response(False, "User does not exist. Please sign up first.", status_code=404)

#         otp = generate_otp()
#         user.otp = otp
#         user.otp_created_at = timezone.now()
#         user.save()

#         print(f"[DEBUG] OTP for {phone}: {otp}")
#         return api_response(True, "OTP sent to phone", data={"otp": otp})


# #  Verify Login OTP


# class VerifyPhoneOTP(APIView):
#     def post(self, request):
#         otp_input = request.data.get("otp")

#         serializer = UserSerializer(data=request.data, partial=True)
#         if not serializer.is_valid():
#             return api_response(False, "Validation error", data=serializer.errors, status_code=400)

#         phone = serializer.validated_data.get("phone")

#         user = User.objects.filter(phone=phone, otp=otp_input).first()
#         if user and user.is_otp_valid(otp_input):
#             tokens = get_tokens_for_user(user)
#             user_data = UserSerializer(user).data
#             return api_response(True, "Login successful", data={
#                 "token": tokens["refresh"],
#                 "user": user_data
#             })

#         return api_response(False, "Invalid or expired OTP", status_code=400)


# #  Collect Signup Data and Send OTP
# class SignupRequest(APIView):
#     def post(self, request):
#         serializer = UserSerializer(data=request.data)
#         if not serializer.is_valid():
#             return api_response(False, "Validation error", data=serializer.errors, status_code=400)

#         data = serializer.validated_data
#         phone = data.get('phone')
#         email = data.get('email')

#         if User.objects.filter(phone=phone).exists():
#             return api_response(False, "Phone already registered", status_code=400)

#         if email and User.objects.filter(email=email).exists():
#             return api_response(False, "Email already registered", status_code=400)

#         otp = generate_otp()

#         request.session["signup_data"] = data
#         request.session["signup_otp"] = otp
#         request.session["signup_otp_time"] = timezone.now().isoformat()

#         print(f"[DEBUG] Signup OTP for {phone}: {otp}")
#         return api_response(True, "OTP sent for verification", data={"otp": otp})


# class FinalizeSignup(APIView):
#     def post(self, request):
#         otp_input = request.data.get("otp")
#         signup_data = request.session.get("signup_data")
#         otp_sent = request.session.get("signup_otp")
#         otp_time_str = request.session.get("signup_otp_time")

#         # Step 1: Check if session data is valid
#         if not signup_data or not otp_sent or not otp_time_str:
#             return api_response(False, "Signup session expired or invalid", status_code=400)

#         # Step 2: Verify OTP
#         if otp_input != otp_sent:
#             return api_response(False, "Invalid OTP", status_code=400)

#         # Step 3: Check if OTP is expired (older than 5 minutes)
#         otp_created = timezone.datetime.fromisoformat(otp_time_str)
#         if (timezone.now() - otp_created).total_seconds() > 300:
#             return api_response(False, "OTP expired", status_code=400)

#         # Step 4: Revalidate the signup data using serializer
#         serializer = UserSerializer(data=signup_data)
#         if not serializer.is_valid():
#             return api_response(False, "Signup data invalid", data=serializer.errors, status_code=400)

#         # Step 5: Create the user with validated data
#         user = User.objects.create(**serializer.validated_data)

#         # Step 6: Clear session data
#         for key in ["signup_data", "signup_otp", "signup_otp_time"]:
#             request.session.pop(key, None)

#         # Step 7: Return JWT tokens and user info
#         tokens = get_tokens_for_user(user)
#         user_data = UserSerializer(user).data

#         print(f"[DEBUG] User created: {user.phone} - {user.name or 'Unregistered'}")

#         return api_response(True, "User registered successfully", data={
#             "token": tokens["refresh"],
#             "user": user_data
#         })



# class ProfileView(APIView):
#     permission_classes = [IsAuthenticated]

#     def put(self, request):
#         user = request.user
#         serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)

#         if serializer.is_valid():
#             serializer.save()
#             return api_response(True, "Profile updated successfully", data=serializer.data)

#         return api_response(False, "Validation error", data=serializer.errors, status_code=400)

