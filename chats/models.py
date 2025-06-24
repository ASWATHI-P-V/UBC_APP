# messages/models.py
from django.db import models
from accounts.models import User # Import your User model from the accounts app

class Message(models.Model):
    """
    Represents a direct message between two users.
    """
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False) # To track if the message has been read

    class Meta:
        ordering = ['-timestamp'] # Order messages by newest first
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        # Displays the first 50 characters of the message content
        return f"From {self.sender.name} to {self.receiver.name}: {self.content[:50]}..."