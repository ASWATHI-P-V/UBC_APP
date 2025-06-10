from django.db import models
from accounts.models import User  # Adjust if your user model import is different

class SocialMediaPlatform(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=255)  # Can store icon class or path
    data_type = models.CharField(max_length=20, choices=[("url", "URL"), ("phone", "Phone Number")])

    def __str__(self):
        return self.name

class SocialMediaLink(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="social_links")
    platform = models.ForeignKey(SocialMediaPlatform, on_delete=models.CASCADE)
    data = models.CharField(max_length=255)  # URL or phone number

    def __str__(self):
        return f"{self.user.mobile_number} - {self.platform.name}"
