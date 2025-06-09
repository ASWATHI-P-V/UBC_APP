from django.db import models

class Category(models.Model):
    CATEGORY_TYPE_CHOICES = (
        ('professional', 'Professional'),
        ('business', 'Business'),
    )

    id = models.AutoField(primary_key=True)
    icon = models.ImageField(upload_to='category_icons/')
    category_name = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=20, choices=CATEGORY_TYPE_CHOICES)

    def __str__(self):
        return self.category_name
