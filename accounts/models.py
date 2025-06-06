from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, name, mobile_number, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        if not mobile_number:
            raise ValueError('Users must have a mobile number')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, mobile_number=mobile_number, **extra_fields)
        user.set_password(password or '')  # Use hashed password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, mobile_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not password:
            password = 'admin'  # for testing only; NEVER use in production

        return self.create_user(email, name, mobile_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin): 
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    mobile_number = models.CharField(max_length=20, unique=True,null=True, blank=True)
    is_whatsapp = models.BooleanField(default=False,null=True, blank=True)
    country_code = models.CharField(max_length=5, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    otp = models.CharField(max_length=6, unique=True, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)

    ROLE_CHOICES = (
        ('individual', 'Individual'),
        ('business', 'Business'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='individual')

    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    category = models.TextField(null=True, blank=True)
    enable_designation_and_company_name = models.BooleanField(default=False,null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    about = models.TextField(null=True, blank=True)

    business_name = models.CharField(max_length=255, null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'mobile_number'  # Use phone to log in
    REQUIRED_FIELDS = ['name', 'email']  # Shown when creating superuser

    def is_otp_valid(self, otp_input, expiry_seconds=300):
        if self.otp != otp_input or not self.otp_created_at:
            return False
        return (timezone.now() - self.otp_created_at).total_seconds() <= expiry_seconds

    def __str__(self):
        return f"{self.mobile_number} - {self.name or 'Unregistered'}"


