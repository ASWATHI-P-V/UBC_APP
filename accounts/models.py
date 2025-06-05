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

        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True.')

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




















# from django.db import models
# from django.utils import timezone

# class User(models.Model):
#     name = models.CharField(max_length=100,null=True, blank=True)
#     email = models.EmailField(unique=True, null=True, blank=True)
#     phone = models.CharField(max_length=20, unique=True)  # Supports country code
#     is_whatsapp = models.BooleanField(default=False)
#     country_code = models.CharField(max_length=5, null=True, blank=True)

#     # OTP fields
#     otp = models.CharField(max_length=6, unique=True, null=True, blank=True)
#     otp_created_at = models.DateTimeField(null=True, blank=True)

#     def is_otp_valid(self, otp_input, expiry_seconds=300):
#         if self.otp != otp_input or not self.otp_created_at:
#             return False
#         return (timezone.now() - self.otp_created_at).total_seconds() <= expiry_seconds

#     def __str__(self):
#         return f"{self.phone} - {self.name or 'Unregistered'}"



# from django.utils import timezone
# from django.db import models
# from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission


# class UserManager(BaseUserManager):
#     def create_user(self, email, name, password=None, **extra_fields):
#         if not email:
#             raise ValueError('Users must have an email address')
        
#         email = self.normalize_email(email)
        
#         # For regular users, set password if provided (or keep blank for OTP-based login)
#         user = self.model(email=email, name=name, **extra_fields)
#         if password:
#             user.set_password(password)
#         else:
#             user.password = ''  # For OTP-only auth

#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email, name, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         extra_fields.setdefault('is_active', True)
#         extra_fields.setdefault('role', 'admin')  # 👈 Required fix for your DB error

#         if not extra_fields.get('is_staff'):
#             raise ValueError('Superuser must have is_staff=True.')
#         if not extra_fields.get('is_superuser'):
#             raise ValueError('Superuser must have is_superuser=True.')

#         user = self.create_user(email, name, password=password, **extra_fields)
#         return user


# class User(AbstractBaseUser, PermissionsMixin):
#     # Core
#     email = models.EmailField(unique=True, null=True, blank=True)
#     name = models.CharField(max_length=255, null=True, blank=True)
#     phone = models.CharField(max_length=20, null=True, blank=True)
#     country_code = models.CharField(max_length=5, null=True, blank=True)
#     is_whatsapp = models.BooleanField(default=False)
#     address = models.TextField(blank=True, null=True)

#     # Optional password (for AbstractBaseUser compatibility)
#     password = models.CharField(max_length=128, blank=True, default='')

#     # OTP Fields
#     otp = models.CharField(max_length=6, unique=True, null=True, blank=True)
#     otp_created_at = models.DateTimeField(null=True, blank=True)

#     def is_otp_valid(self, otp_input, expiry_seconds=300):
#         if self.otp != otp_input or not self.otp_created_at:
#             return False
#         return (timezone.now() - self.otp_created_at).total_seconds() <= expiry_seconds

#     # Profile
#     ROLE_CHOICES = (
#         ('individual', 'Individual'),
#         ('business', 'Business'),
#     )
#     role = models.CharField(max_length=20, choices=ROLE_CHOICES, null=True, blank=True)
#     profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
#     category = models.CharField(max_length=100, blank=True, null=True)
#     designation = models.CharField(max_length=100, blank=True, null=True)
#     about = models.TextField(blank=True, null=True)
#     enable_destination_and_company_name = models.BooleanField(default=False)

#     # Business
#     business_name = models.CharField(max_length=255, blank=True, null=True)
#     company_name = models.CharField(max_length=255, blank=True, null=True)
#     logo = models.ImageField(upload_to='logos/', blank=True, null=True)

#     # Permissions
#     groups = models.ManyToManyField(
#         Group,
#         related_name='custom_user_set',
#         blank=True,
#         help_text='The groups this user belongs to.',
#         verbose_name='groups',
#     )
#     user_permissions = models.ManyToManyField(
#         Permission,
#         related_name='custom_user_permissions',
#         blank=True,
#         help_text='Specific permissions for this user.',
#         verbose_name='user permissions',
#     )

#     # Admin
#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)
#     is_superuser = models.BooleanField(default=False)

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['name']

#     objects = UserManager()

#     def __str__(self):
#         return f"{self.phone} - {self.name or 'Unregistered'}"
