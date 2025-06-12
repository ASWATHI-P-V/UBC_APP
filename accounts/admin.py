from django.contrib import admin
from .models import User, ProfileViewRecord
from category.models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category_name', 'type')  # ✅ use correct field
    search_fields = ('category_name',)
    list_filter = ('type',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'mobile_number', 'email', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('name', 'email', 'mobile_number')
    readonly_fields = ('profile_views', 'otp_created_at')
    fieldsets = (
        ("Basic Info", {
            "fields": ('name', 'email', 'mobile_number', 'country_code', 'is_whatsapp', 'address'),
        }),
        ("Profile & Role", {
            "fields": ('role', 'category', 'profile_picture', 'about', 'enable_designation_and_company_name', 'designation'),
        }),
        ("Business Info", {
            "fields": ('business_name', 'company_name', 'logo'),
        }),
        ("Security & Status", {
            "fields": ('otp', 'otp_created_at', 'is_active', 'is_staff', 'is_superuser'),
        }),
        ("Analytics", {
            "fields": ('profile_views',),
        }),
    )


@admin.register(ProfileViewRecord)
class ProfileViewRecordAdmin(admin.ModelAdmin):
    list_display = ('profile_owner', 'viewer', 'viewed_at')
    list_filter = ('viewed_at',)
    search_fields = ('profile_owner__mobile_number', 'viewer__mobile_number')











# from django.contrib import admin
# from .models import User,ProfileViewRecord
# from .models import Category


# admin.site.register(Category)
# admin.site.register(User)
# admin.site.register(ProfileViewRecord)

