from django.db import models
from django.conf import settings
# from accounts.models import User 

class SocialMediaPlatform(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.ImageField(upload_to='platform_icons/', null=True, blank=True)
    data_type = models.CharField(max_length=20, choices=[("url", "URL"), ("phone", "Phone Number")])

    def __str__(self):
        return self.name

class SocialMediaLink(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="social_links")
    platform = models.ForeignKey(SocialMediaPlatform, on_delete=models.CASCADE)
    platform_url = models.CharField(max_length=255)  # URL or phone number

    def __str__(self):
        return f"{self.user.mobile_number} - {self.platform.name}"
