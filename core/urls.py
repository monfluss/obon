from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.urls import path
from .views import create_admin # импортируй функцию из своего views

urlpatterns = [
    # ... твои другие пути ...
    path('make-admin/', create_admin),
]
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('streaming.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)