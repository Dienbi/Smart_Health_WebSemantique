"""
URL configuration for Smart Health Web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/ai/', include('apps.ai_service.urls')),
    
    # Add more API endpoints here as they are created
    # path('api/users/', include('apps.users.urls')),
    # path('api/activities/', include('apps.activities.urls')),
    # path('api/health-records/', include('apps.health_records.urls')),
    # path('api/meals/', include('apps.meals.urls')),
    # path('api/habits/', include('apps.habits.urls')),
    # path('api/defis/', include('apps.defis.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
