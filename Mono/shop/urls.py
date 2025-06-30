from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from shop import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.store.urls')),
    path('api/v1/', include('apps.users.urls')),
    path('tg/', include('apps.common.urls')),
    path('api/v2/', include('apps.ninja_api.urls')),
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
