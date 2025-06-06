from rest_framework import serializers
from .models import ImageUpload
from .validators import ImageSizeValidator, ImageDimensionValidator, image_extension_validator



class ImageUploadSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ImageUpload
        fields = ['id', 'image_url']

    def get_image_url(self, obj):
        return obj.get_image_url()


# class ImageUploadSerializer(serializers.ModelSerializer):
#     image_url = serializers.SerializerMethodField()
    
#     class Meta:
#         model = ImageUpload
#         fields = [
#             'id', 'image', 'original_filename', 'title', 'description',
#             'width', 'height', 'file_size', 'uploaded_at', 'updated_at', 'image_url'
#         ]
#         read_only_fields = [
#             'id', 'original_filename', 'width', 'height', 'file_size',
#             'uploaded_at', 'updated_at'
#         ]
    
#     def get_image_url(self, obj):
#         return obj.get_image_url()
    
#     def validate_image(self, value):
#         # Validate file extension
#         image_extension_validator(value)
        
#         # Validate file size (5MB max)
#         ImageSizeValidator(max_size_mb=5)(value)
        
#         # Validate image dimensions
#         ImageDimensionValidator(max_width=4000, max_height=4000)(value)
        
#         return value