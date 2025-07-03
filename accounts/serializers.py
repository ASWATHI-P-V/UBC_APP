# serializers.py
from rest_framework import serializers
import phonenumbers
from .models import User
from media_management.models import ImageUpload
from media_management.serializers import ImageUploadSerializer
from category.models import Category
from category.serializers import CategorySerializer
from django.contrib.auth import get_user_model
from social.serializers import SocialMediaLinkSerializer
from django.db import models


class UserSerializer(serializers.ModelSerializer):
    profileupdate_completed = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'mobile_number', 'country_code', 'is_whatsapp', 'profileupdate_completed', 'profile_picture', 'role', 'about']

    def get_profileupdate_completed(self, obj):
        # Required fields for all users
        required_fields = ['name', 'mobile_number', 'address', 'role', 'profile_picture', 'category']

        # Additional fields required if role is 'business'
        if obj.role == 'business':
            required_fields += ['business_name', 'logo']

        for field in required_fields:
            value = getattr(obj, field, None)
            if not value:
                return False
        return True

    def validate(self, attrs):
        role = attrs.get('role', None)
        if role == 'business':
            if not attrs.get('business_name'):
                raise serializers.ValidationError({"business_name": "This field is required for business role."})
            if not attrs.get('logo'):
                raise serializers.ValidationError({"logo": "This field is required for business role."})
        return attrs

    def update(self, instance, validated_data):
        image_file = validated_data.pop('image_file', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if image_file:
            ImageUpload.objects.create(user=instance, image=image_file)

        instance = User.objects.prefetch_related('uploaded_images').get(id=instance.id)
        return instance

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        # Strip country code prefix from mobile_number for output only
        mobile = rep.get("mobile_number")
        country_code = rep.get("country_code")

        if mobile and country_code and mobile.startswith(country_code):
            rep["mobile_number"] = mobile[len(country_code):]

        return rep


    def validate(self, attrs):
        mobile_number = attrs.get('mobile_number')
        country_code = attrs.get('country_code')
        
        # Check if phone is already in E164 format (starts with +)
        if mobile_number and mobile_number.startswith('+'):
            try:
                parsed = phonenumbers.parse(mobile_number, None)
                if phonenumbers.is_valid_number(parsed):
                    # Phone is already formatted, just ensure country_code matches
                    attrs['mobile_number'] = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
                    attrs['country_code'] = f"+{parsed.country_code}"
                    return attrs
            except phonenumbers.NumberParseException:
                pass
        
        # Original validation logic for non-formatted numbers
        if not mobile_number or not country_code:
            raise serializers.ValidationError("Mobile number and country code are required.")
        
        # Combine the country code and phone
        full_phone = f"{country_code}{mobile_number}"
        try:
            parsed = phonenumbers.parse(full_phone, None)
        except phonenumbers.NumberParseException as e:
            raise serializers.ValidationError(f"Mobile number could not be parsed: {e}")
        
        if not phonenumbers.is_valid_number(parsed):
            raise serializers.ValidationError("Mobile number is invalid.")
        
        # Replace the plain phone with the formatted international version
        attrs['mobile_number'] = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        attrs['country_code'] = f"+{parsed.country_code}"
        
        return attrs

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(
        source='category',
        queryset=Category.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    category = CategorySerializer(read_only=True)
    image_file = serializers.ImageField(write_only=True, required=False)
    profileupdate_completed = serializers.SerializerMethodField(read_only=True)
    social_links = SocialMediaLinkSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'name', 'email', 'mobile_number', 'address', 'role', 'profile_picture', 'category', 'category_id',
            'designation', 'about', 'social_links', 'enable_designation_and_company_name', 'business_name',
            'company_name', 'logo',
            'image_file', 'profile_views', 'profileupdate_completed'
        ]
        extra_kwargs = {
            'category_id': {'write_only': True},
            # We set required=False here because the actual requirement is enforced in the validate method
            'profile_picture': {'required':True},
            'logo': {'required': False, 'allow_null': True},
        }

    def get_profileupdate_completed(self, obj):
        required_fields = ['name', 'mobile_number', 'address', 'role', 'profile_picture', 'category']

        if obj.role == 'business':
            required_fields += ['business_name', 'logo']

        for field_name in required_fields:
            value = getattr(obj, field_name, None)

            if hasattr(User, field_name) and isinstance(getattr(User, field_name).field, models.ImageField):
                if not value or not bool(value.name):
                    return False
            elif not value:
                return False
        return True

    def validate(self, attrs):
        instance = self.instance

        current_role = attrs.get('role', instance.role if instance else None)

        if current_role is None and instance is None:
             raise serializers.ValidationError({"role": "Role is required."})

        # --- Validation for 'business' role ---
        if current_role == 'business':
            business_name = attrs.get('business_name', instance.business_name if instance else None)
            if not business_name:
                raise serializers.ValidationError({"business_name": "Business name is required for business role."})

            # CONDITION 2: LOGO IS REQUIRED FOR BUSINESS ROLE
            logo = attrs.get('logo', instance.logo if instance else None)
            if not logo and (instance is None or not instance.logo):
                raise serializers.ValidationError({"logo": "Logo is required for business role."})

            # Clear individual-specific fields if transitioning from individual to business
            if instance and instance.role == 'individual' and 'role' in attrs and attrs['role'] == 'business':
                attrs['designation'] = None
                attrs['about'] = None
                # No need to clear profile_picture here, as it's universally required now

        # --- Validation for 'individual' role ---
        elif current_role == 'individual':
            # Clear business-specific fields if transitioning from business to individual
            if instance and instance.role == 'business' and 'role' in attrs and attrs['role'] == 'individual':
                attrs['business_name'] = None
                attrs['company_name'] = None
                attrs['logo'] = None

        # --- General validation for all roles ---
        # CONDITION 1: PROFILE PICTURE IS REQUIRED FOR ALL ROLES
        profile_picture = attrs.get('profile_picture', instance.profile_picture if instance else None)
        if not profile_picture and (instance is None or not instance.profile_picture):
            raise serializers.ValidationError({"profile_picture": "Profile picture is required."})

        # Other general validations
        name = attrs.get('name', instance.name if instance else None)
        if not name:
            raise serializers.ValidationError({"name": "Name is required."})

        address = attrs.get('address', instance.address if instance else None)
        if not address:
            raise serializers.ValidationError({"address": "Address is required."})

        category = attrs.get('category', instance.category if instance else None)
        if not category:
            raise serializers.ValidationError({"category": "Category is required."})

        return attrs

    def update(self, instance, validated_data):
        image_file = validated_data.pop('image_file', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if image_file:
            ImageUpload.objects.create(user=instance, image=image_file)

        return instance


# class UserProfileUpdateSerializer(serializers.ModelSerializer):
#     category_id = serializers.PrimaryKeyRelatedField(
#         source='category',
#         queryset=Category.objects.all(),
#         write_only=True,
#         required=False
#     )
#     category = CategorySerializer(read_only=True)
#     image_file = serializers.ImageField(write_only=True, required=False)
#     profileupdate_completed = serializers.SerializerMethodField(read_only=True)

#     class Meta:
#         model = User
#         fields = [
#             'name','email', 'mobile_number', 'address', 'role', 'profile_picture', 'category','category_id',  
#             'designation', 'about', 'social_links','enable_designation_and_company_name', 'business_name',
#             'company_name', 'logo', 
#             'image_file', 'profile_views','profileupdate_completed'  
#         ]
#         extra_kwargs = {
#             'category_id': {'write_only': True},
#             'profile_picture': {'required': False, 'allow_null': True},
#             'logo': {'required': False, 'allow_null': True},
#         }
#     def get_profileupdate_completed(self, obj):
#         # This method is for read-only display, not for validation during PUT/PATCH.
#         # It checks if profile is "complete" for display purposes.
#         required_fields = ['name', 'mobile_number', 'address', 'role', 'profile_picture', 'category']

#         if obj.role == 'business':
#             required_fields += ['business_name', 'logo']

#         for field in required_fields:
#             value = getattr(obj, field, None)
#             # For ImageFields, check if a file is actually associated
#             if isinstance(getattr(User, field).field, models.ImageField):
#                 if not value or not bool(value.name): # Check if image field has a file name
#                     return False
#             elif not value:
#                 return False
#         return True


#     def validate(self, attrs):
#         # Get the current instance (if it's an update)
#         instance = self.instance

#         # Determine the role: either from the incoming data or the existing instance
#         # If 'role' is provided in attrs, use that. Otherwise, use the instance's role.
#         # If it's a creation, instance will be None, and attrs.get('role') will be used.
#         current_role = attrs.get('role', instance.role if instance else None)

#         # Ensure role is set for new users or if being updated
#         if current_role is None and instance is None: # For creation if role is not provided
#              raise serializers.ValidationError({"role": "Role is required."})


#         # --- Validation for 'business' role ---
#         if current_role == 'business':
#             # Check business_name
#             business_name = attrs.get('business_name', instance.business_name if instance else None)
#             if not business_name:
#                 raise serializers.ValidationError({"business_name": "Business name is required for business role."})

#             # Check logo
#             logo = attrs.get('logo', instance.logo if instance else None)
#             # If logo is being updated or was never set, and no new logo is provided
#             if not logo and (instance is None or not instance.logo):
#                 raise serializers.ValidationError({"logo": "Logo is required for business role."})

#             # Clear individual-specific fields if transitioning from individual to business
#             if instance and instance.role == 'individual' and 'role' in attrs and attrs['role'] == 'business':
#                 attrs['designation'] = None
#                 attrs['about'] = None
#                 # Add other individual-specific fields to clear if they exist

#         # --- Validation for 'individual' role ---
#         elif current_role == 'individual':
#             # Check profile_picture for individual role (if it's a required field for them)
#             profile_picture = attrs.get('profile_picture', instance.profile_picture if instance else None)
#             # If profile_picture is being updated or was never set, and no new picture is provided
#             if not profile_picture and (instance is None or not instance.profile_picture):
#                 raise serializers.ValidationError({"profile_picture": "Profile picture is required for individual role."})

#             # Clear business-specific fields if transitioning from business to individual
#             if instance and instance.role == 'business' and 'role' in attrs and attrs['role'] == 'individual':
#                 attrs['business_name'] = None
#                 attrs['company_name'] = None
#                 attrs['logo'] = None
#                 # Add other business-specific fields to clear if they exist

#         # General validation for 'name' and 'address' (if required for both)
#         # You can add more general checks here
#         name = attrs.get('name', instance.name if instance else None)
#         if not name:
#             raise serializers.ValidationError({"name": "Name is required."})

#         address = attrs.get('address', instance.address if instance else None)
#         if not address:
#             raise serializers.ValidationError({"address": "Address is required."})

#         # Category check (if required for all roles)
#         category = attrs.get('category', instance.category if instance else None)
#         if not category:
#             raise serializers.ValidationError({"category": "Category is required."})


#         return attrs

#     def update(self, instance, validated_data):
#         image_file = validated_data.pop('image_file', None)

#         # Handle updating many-to-many fields if you had them (e.g., social_links)
#         # social_links_data = validated_data.pop('social_links', None)
#         # if social_links_data is not None:
#         #     instance.social_links.set(social_links_data) # Or add/remove as needed

#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()

#         if image_file:
#             # Assuming ImageUpload model exists and handles profile_picture or other image uploads
#             # If image_file is meant for profile_picture, you might set instance.profile_picture = image_file
#             # and save directly, or use ImageUpload if it's for a gallery.
#             # For now, keeping your original ImageUpload logic.
#             ImageUpload.objects.create(user=instance, image=image_file)

#         # Pre-fetch related data for the response, if necessary for the serializer's output
#         # instance = User.objects.prefetch_related('uploaded_images').get(id=instance.id)
#         # If 'social_links' is a ManyToManyField, you might need to prefetch it here
#         # instance = User.objects.prefetch_related('social_links').get(id=instance.id)
#         return instance


User = get_user_model() # Get the currently active user model
class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email']
        # Add any other fields you want to expose for the user list
        # For example, if you have a 'role' field directly on your User model:
        # fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'role']

# Keep your existing UserProfileUpdateSerializer as is for profile updates.
# from .models import UserProfile # Assuming UserProfile is where extra user data is
# class UserProfileUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User # or UserProfile if you have a separate profile model
#         fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'bio', 'profile_picture', 'role', 'logo']
#  

# social service and theme

# social put