# serializers.py
from rest_framework import serializers
import phonenumbers
from .models import User
from media_management.models import ImageUpload
from media_management.serializers import ImageUploadSerializer
from category.models import Category
from category.serializers import CategorySerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'mobile_number', 'country_code', 'is_whatsapp']
    
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
        required=False
    )
    category = CategorySerializer(read_only=True)
    image_file = serializers.ImageField(write_only=True, required=False)
    

    class Meta:
        model = User
        fields = [
            'name', 'mobile_number', 'address', 'role', 'profile_picture', 'category','category_id',   # for input
            'designation', 'about', 'enable_designation_and_company_name', 'business_name',
            'company_name', 'logo',
            'image_file', 'profile_views'
        ]
        extra_kwargs = {
            'category_id': {'write_only': True},
        }

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


# class UserProfileUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = [
#             'name', 'mobile_number', 'address', 'role', 'profile_picture', 'category',
#             'designation', 'about', 'enable_designation_and_company_name', 'business_name',
#             'company_name', 'logo'
#         ]

#     def validate(self, attrs):
#         role = attrs.get('role', None)

#         if role == 'business':
#             if not attrs.get('business_name'):
#                 raise serializers.ValidationError({"business_name": "This field is required for business role."})
#             if not attrs.get('logo'):
#                 raise serializers.ValidationError({"logo": "This field is required for business role."})

#         return attrs


