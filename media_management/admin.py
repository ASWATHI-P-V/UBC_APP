from django.contrib import admin
from .models import ImageUpload

@admin.register(ImageUpload)
class ImageUploadAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'user', 'width', 'height', 'file_size', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['original_filename', 'user__name', 'user__mobile_number', 'title']
    readonly_fields = ['id', 'original_filename', 'width', 'height', 'file_size', 'uploaded_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')