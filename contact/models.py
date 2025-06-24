from django.db import models
from accounts.models import User

class SavedContact(models.Model):
    """
    Represents a contact saved by a specific user.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_contact_entries')
    saved_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_by_entries')
    saved_at = models.DateTimeField(auto_now_add=True)
    # You can add more fields here, e.g., 'notes', 'category_for_this_contact'

    class Meta:
        unique_together = ('user', 'saved_user') # A user can save another user only once
        verbose_name = "Saved Contact"
        verbose_name_plural = "Saved Contacts"

    def __str__(self):
        return f"{self.user.name} saved {self.saved_user.name}"