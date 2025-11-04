from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DefiViewSet, ParticipationViewSet, challenge_list_view

router = DefaultRouter()
router.register(r'defis', DefiViewSet, basename='defi')
router.register(r'participations', ParticipationViewSet, basename='participation')

app_name = 'defis'

urlpatterns = [
    # Web interface URLs
    path('', challenge_list_view, name='challenge-list'),
    
    # API URLs
    path('api/', include(router.urls)),
]
