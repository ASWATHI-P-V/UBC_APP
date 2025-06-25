# notifications/models.py

from django.db import models
from accounts.models import User # Import your User model

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('system', 'System Message'),
        ('announcement', 'Announcement'),
        ('alert', 'Alert'),
        ('info', 'Information'),
        ('custom', 'Custom'),
        # Add more types as needed
    ]

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text="The user who receives this notification."
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.SET_NULL, # If sender user is deleted, notification remains but sender becomes null
        related_name='sent_notifications',
        null=True,
        blank=True,
        help_text="The user (e.g., admin) who sent this notification (optional)."
    )
    title = models.CharField(
        max_length=255,
        help_text="A short, catchy title for the notification."
    )
    message = models.TextField(
        help_text="The full content of the notification."
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="The date and time the notification was created."
    )
    is_read = models.BooleanField(
        default=False,
        help_text="Indicates whether the recipient has read the notification."
    )
    link = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="An optional URL related to the notification (e.g., a link to a new feature)."
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='system',
        help_text="Categorizes the type of notification."
    )

    class Meta:
        ordering = ['-timestamp'] # Newest notifications first
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"Notification for {self.recipient.name}: {self.title}"