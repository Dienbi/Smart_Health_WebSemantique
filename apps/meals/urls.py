from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MealViewSet, FoodItemViewSet,
    BreakfastViewSet, LunchViewSet, DinnerViewSet, SnackViewSet,
    meal_list_view, meal_create_view, meal_detail_view, meal_update_view, meal_delete_view
)

router = DefaultRouter()
router.register(r'meals', MealViewSet, basename='meal-api')
router.register(r'food-items', FoodItemViewSet, basename='fooditem-api')
router.register(r'breakfast', BreakfastViewSet, basename='breakfast-api')
router.register(r'lunch', LunchViewSet, basename='lunch-api')
router.register(r'dinner', DinnerViewSet, basename='dinner-api')
router.register(r'snack', SnackViewSet, basename='snack-api')

app_name = 'meals'

urlpatterns = [
    # Web interface URLs (MUST come first to take priority)
    path('', meal_list_view, name='meal-list'),
    path('create/', meal_create_view, name='meal-create'),
    path('<int:pk>/edit/', meal_update_view, name='meal-edit'),
    path('<int:pk>/delete/', meal_delete_view, name='meal-delete'),
    path('<int:pk>/', meal_detail_view, name='meal-detail'),
    
    # API URLs
    path('api/', include(router.urls)),
]
