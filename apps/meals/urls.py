from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MealViewSet, FoodItemViewSet,
    BreakfastViewSet, LunchViewSet, DinnerViewSet, SnackViewSet,
    meal_list_view
)

router = DefaultRouter()
router.register(r'meals', MealViewSet, basename='meal')
router.register(r'food-items', FoodItemViewSet, basename='fooditem')
router.register(r'breakfast', BreakfastViewSet, basename='breakfast')
router.register(r'lunch', LunchViewSet, basename='lunch')
router.register(r'dinner', DinnerViewSet, basename='dinner')
router.register(r'snack', SnackViewSet, basename='snack')

app_name = 'meals'

urlpatterns = [
    # Web interface URLs
    path('', meal_list_view, name='meal-list'),
    
    # API URLs
    path('api/', include(router.urls)),
]
