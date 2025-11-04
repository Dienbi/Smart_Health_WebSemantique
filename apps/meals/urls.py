from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MealViewSet, FoodItemViewSet,
    BreakfastViewSet, LunchViewSet, DinnerViewSet, SnackViewSet
)

router = DefaultRouter()
router.register(r'meals', MealViewSet, basename='meal')
router.register(r'food-items', FoodItemViewSet, basename='fooditem')
router.register(r'breakfast', BreakfastViewSet, basename='breakfast')
router.register(r'lunch', LunchViewSet, basename='lunch')
router.register(r'dinner', DinnerViewSet, basename='dinner')
router.register(r'snack', SnackViewSet, basename='snack')

urlpatterns = [
    path('', include(router.urls)),
]
