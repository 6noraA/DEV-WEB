from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from monapp.admin import admin_site

urlpatterns = [
    path('admin/', admin.site.urls),           # Django admin original (superuser)
    path('maville-admin/', admin_site.urls),   # Admin custom (admins du site)
    path('', include('monapp.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)