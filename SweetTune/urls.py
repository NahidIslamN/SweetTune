
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('auths.urls')),
    path('api/v1/', include('chats.urls')),
    path('api/v1/profiles/', include('profiles.urls')),
    path('api/v1/users/', include('databases_models.urls')),
    path('api/v1/amazon_api/', include('amazon_api.urls'))
]
# path('blog/', include('amazon_api.urls'))

if settings.DEBUG:
       
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
