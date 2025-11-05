"""
Backoffice (Admin) URLs for Meals app - FoodItem CRUD management
"""
from django.urls import path
from .views import (
    AdminFoodItemListView,
    AdminFoodItemDetailView,
    AdminFoodItemCreateView,
    AdminFoodItemUpdateView,
    AdminFoodItemDeleteView,
)

app_name = 'meals_admin'

urlpatterns = [
    # FoodItem CRUD
    path('', AdminFoodItemListView.as_view(), name='list'),
    path('create/', AdminFoodItemCreateView.as_view(), name='create'),
    path('<int:pk>/', AdminFoodItemDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', AdminFoodItemUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', AdminFoodItemDeleteView.as_view(), name='delete'),
]

