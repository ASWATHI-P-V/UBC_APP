from django.db import models
from django.conf import settings

class Theme(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='theme')
    background_image = models.ImageField(upload_to='theme/backgrounds/', blank=True, null=True)
    background_color = models.CharField(max_length=20, default="#ffffff")  # white
    font_color = models.CharField(max_length=20, default="#000000")        # black

    def __str__(self):
        return f"{self.user}'s Theme"
