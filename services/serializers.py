from rest_framework import serializers
from .models import Service

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'user', 'name', 'picture', 'description', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
