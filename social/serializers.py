from rest_framework import serializers
from .models import SocialMediaLink, SocialMediaPlatform

class SocialMediaPlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMediaPlatform
        fields = ['id', 'name', 'icon', 'data_type']

class SocialMediaLinkSerializer(serializers.ModelSerializer):
    platform = SocialMediaPlatformSerializer(read_only=True)
    platform_id = serializers.PrimaryKeyRelatedField(
        queryset=SocialMediaPlatform.objects.all(),
        write_only=True,
        source='platform'
    )

    class Meta:
        model = SocialMediaLink
        fields = ['id', 'user', 'platform', 'platform_id', 'data']
        read_only_fields = ['user']

    def create(self, validated_data):
        print("validated_data:", validated_data)
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
