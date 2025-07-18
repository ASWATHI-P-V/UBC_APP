from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings 
from django.conf.urls.static import static

urlpatterns = [
    # path('grappelli/', include('grappelli.urls')),
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/category/', include('category.urls')),
    path('api/social/', include('social.urls')),
    path('api/services/', include('services.urls')),
    path('api/theme/', include('theme.urls')),
    path('api/contact/', include('contact.urls')),
    path('api/chats/', include('chats.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('', lambda request: redirect('/admin/')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    