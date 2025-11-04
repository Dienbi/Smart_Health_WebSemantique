"""
URL configuration for Smart Health Web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.users.views import home_view, login_view, signup_view, logout_view, dashboard_view

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication URLs
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    
    # Web interface URLs
    path('habits/', include('apps.habits.urls', namespace='habits')),
    path('activities/', include('apps.activities.urls', namespace='activities')),
    path('meals/', include('apps.meals.urls', namespace='meals')),
    path('health/', include('apps.health_records.urls', namespace='health_records')),
    path('challenges/', include('apps.defis.urls', namespace='defis')),
    
    # Backoffice URLs
    path('backoffice/defis/', include(('apps.defis.back_urls', 'defis_admin'), namespace='defis_admin')),
    
    # API endpoints
    path('api/ai/', include(('apps.ai_service.urls', 'api_ai'), namespace='api_ai')),
    path('api/users/', include('apps.users.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
