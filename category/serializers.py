from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'icon', 'category_name', 'type']

    def validate_category_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Category name must be at least 2 characters long.")
        
        qs = Category.objects.filter(category_name__iexact=value)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("A category with this name already exists.")
        
        return value.title()

    def validate_type(self, value):
        valid_types = ['professional', 'business']
        if value.lower() not in valid_types:
            raise serializers.ValidationError(f"Type must be one of: {', '.join(valid_types)}")
        return value.lower()

    def validate(self, data):
        name = data.get('category_name', '').lower()
        if data.get('type') == 'business' and 'personal' in name:
            raise serializers.ValidationError({
                'category_name': "Business categories cannot contain 'personal' in the name."
            })
        return data


class CategoryIDSerializer(serializers.Serializer):
    """Validate a single category ID exists."""
    id = serializers.IntegerField()

    def validate_id(self, value):
        if not Category.objects.filter(pk=value).exists():
            raise serializers.ValidationError(f"Category with ID {value} does not exist.")
        return value


class CategoryBulkSerializer(serializers.Serializer):
    """Validate a list of category IDs."""
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        error_messages={
            'empty': 'At least one category ID is required.',
            'required': 'Category IDs are required.'
        }
    )

    def validate_ids(self, value):
        non_existing_ids = [i for i in value if not Category.objects.filter(pk=i).exists()]
        if non_existing_ids:
            raise serializers.ValidationError(
                f"Categories with these IDs do not exist: {non_existing_ids}"
            )
        return value

