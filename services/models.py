from django.db import models
from django.conf import settings

class Service(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    picture = models.ImageField(upload_to='service_pictures/')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
