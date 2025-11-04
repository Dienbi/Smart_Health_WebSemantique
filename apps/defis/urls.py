from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DefiViewSet, ParticipationViewSet

router = DefaultRouter()
router.register(r'defis', DefiViewSet, basename='defi')
router.register(r'participations', ParticipationViewSet, basename='participation')

urlpatterns = [
    path('', include(router.urls)),
]
