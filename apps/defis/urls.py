from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DefiViewSet, ParticipationViewSet

router = DefaultRouter()
router.register(r'defis', DefiViewSet, basename='defi')
router.register(r'participations', ParticipationViewSet, basename='participation')

app_name = 'defis'

urlpatterns = [
    # Web interface URLs (from front_urls.py)
    path('', include('apps.defis.front_urls')),
    
    # API URLs
    path('api/', include(router.urls)),
]
