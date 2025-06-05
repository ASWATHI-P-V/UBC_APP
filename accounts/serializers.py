# serializers.py
from rest_framework import serializers
import phonenumbers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'mobile_number', 'country_code', 'is_whatsapp']
    
    def validate(self, attrs):
        mobile_number = attrs.get('mobile_number')
        country_code = attrs.get('country_code')
        
        # Check if phone is already in E164 format (starts with +)
        if mobile_number and mobile_number.startswith('+'):
            try:
                parsed = phonenumbers.parse(mobile_number, None)
                if phonenumbers.is_valid_number(parsed):
                    # Phone is already formatted, just ensure country_code matches
                    attrs['mobile_number'] = mobile_number
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
    class Meta:
        model = User
        fields = [
            'name', 'mobile_number', 'address', 'role', 'profile_picture', 'category',
            'designation', 'about', 'enable_designation_and_company_name', 'business_name',
            'company_name', 'logo'
        ]

    def validate(self, attrs):
        role = attrs.get('role', None)

        if role == 'business':
            if not attrs.get('business_name'):
                raise serializers.ValidationError({"business_name": "This field is required for business role."})
            if not attrs.get('logo'):
                raise serializers.ValidationError({"logo": "This field is required for business role."})

        return attrs









# # serializers.py
# from rest_framework import serializers
# import phonenumbers
# from .models import User

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'name', 'email', 'phone', 'country_code', 'is_whatsapp']
    
#     def validate(self, attrs):
#         phone = attrs.get('phone')
#         country_code = attrs.get('country_code')
        
#         # Check if phone is already in E164 format (starts with +)
#         if phone and phone.startswith('+'):
#             try:
#                 parsed = phonenumbers.parse(phone, None)
#                 if phonenumbers.is_valid_number(parsed):
#                     # Phone is already formatted, just ensure country_code matches
#                     attrs['phone'] = phone
#                     attrs['country_code'] = f"+{parsed.country_code}"
#                     return attrs
#             except phonenumbers.NumberParseException:
#                 pass
        
#         # Original validation logic for non-formatted numbers
#         if not phone or not country_code:
#             raise serializers.ValidationError("Phone and country code are required.")
        
#         # Combine the country code and phone
#         full_phone = f"{country_code}{phone}"
#         try:
#             parsed = phonenumbers.parse(full_phone, None)
#         except phonenumbers.NumberParseException as e:
#             raise serializers.ValidationError(f"Phone number could not be parsed: {e}")
        
#         if not phonenumbers.is_valid_number(parsed):
#             raise serializers.ValidationError("Phone number is invalid.")
        
#         # Replace the plain phone with the formatted international version
#         attrs['phone'] = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
#         attrs['country_code'] = f"+{parsed.country_code}"
        
#         return attrs



# class UserProfileUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = [
#             'full_name', 'phone', 'address', 'role', 'profile_picture', 'category',
#             'designation', 'about', 'enable_destination_and_company_name', 'business_name',
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