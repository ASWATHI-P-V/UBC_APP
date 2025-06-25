# notifications/admin.py

from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'title', 'timestamp', 'is_read', 'notification_type')
    list_filter = ('is_read', 'notification_type', 'timestamp', 'recipient')
    search_fields = ('title', 'message', 'recipient__name', 'recipient__email')
    raw_id_fields = ('recipient', 'sender') # Use raw_id_fields for ForeignKeys to large tables
    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, "Selected notifications marked as read.")
    mark_as_read.short_description = "Mark selected notifications as read"

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, "Selected notifications marked as unread.")
    mark_as_unread.short_description = "Mark selected notifications as unread"