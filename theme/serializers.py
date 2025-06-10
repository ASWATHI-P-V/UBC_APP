from rest_framework import serializers
from .models import Theme

class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = ['id', 'background_image', 'background_color', 'font_color']
        read_only_fields = ['id']
