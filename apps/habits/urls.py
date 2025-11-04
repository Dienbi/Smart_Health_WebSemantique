from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HabitViewSet, HabitLogViewSet,
    ReadingViewSet, CookingViewSet, DrawingViewSet, JournalingViewSet
)

router = DefaultRouter()
router.register(r'habits', HabitViewSet, basename='habit')
router.register(r'logs', HabitLogViewSet, basename='habitlog')
router.register(r'reading', ReadingViewSet, basename='reading')
router.register(r'cooking', CookingViewSet, basename='cooking')
router.register(r'drawing', DrawingViewSet, basename='drawing')
router.register(r'journaling', JournalingViewSet, basename='journaling')

urlpatterns = [
    path('', include(router.urls)),
]
