from django.contrib import admin
from .models import User
from .models import Category


admin.site.register(Category)
admin.site.register(User)

