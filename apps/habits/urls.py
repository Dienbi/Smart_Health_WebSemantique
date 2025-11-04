from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HabitViewSet, HabitLogViewSet,
    ReadingViewSet, CookingViewSet, DrawingViewSet, JournalingViewSet,
    habit_list_view, habit_logs_view
)

router = DefaultRouter()
router.register(r'', HabitViewSet, basename='habit')
router.register(r'logs', HabitLogViewSet, basename='habitlog')
router.register(r'reading', ReadingViewSet, basename='reading')
router.register(r'cooking', CookingViewSet, basename='cooking')
router.register(r'drawing', DrawingViewSet, basename='drawing')
router.register(r'journaling', JournalingViewSet, basename='journaling')

app_name = 'habits'

urlpatterns = [
    # API URLs (must come first to avoid conflicts)
    path('api/', include(router.urls)),
    
    # Web interface URLs
    path('', habit_list_view, name='habit-list'),
    path('<int:habit_id>/logs/', habit_logs_view, name='habit-logs'),
]
