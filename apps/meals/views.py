from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Meal, FoodItem, Breakfast, Lunch, Dinner, Snack
from .serializers import (
    MealSerializer, FoodItemSerializer,
    BreakfastSerializer, LunchSerializer, DinnerSerializer, SnackSerializer
)


class MealViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Meal model
    """
    queryset = Meal.objects.all()
    serializer_class = MealSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter meals by user if not staff"""
        if self.request.user.is_staff:
            return Meal.objects.all()
        return Meal.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set user from request when creating meal"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_meals(self, request):
        """Get meals for current user"""
        meals = Meal.objects.filter(user=request.user)
        serializer = self.get_serializer(meals, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get meals by type"""
        meal_type = request.query_params.get('type', None)
        if meal_type:
            meals = Meal.objects.filter(user=request.user, meal_type=meal_type.upper())
        else:
            meals = Meal.objects.filter(user=request.user)
        
        serializer = self.get_serializer(meals, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's meals for current user"""
        from django.utils import timezone
        today = timezone.now().date()
        meals = Meal.objects.filter(
            user=request.user,
            meal_date__date=today
        )
        serializer = self.get_serializer(meals, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def food_items(self, request, pk=None):
        """Get all food items for a specific meal"""
        meal = self.get_object()
        food_items = meal.food_items.all()
        serializer = FoodItemSerializer(food_items, many=True)
        return Response(serializer.data)


class FoodItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for FoodItem model
    """
    queryset = FoodItem.objects.all()
    serializer_class = FoodItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter food items by user's meals if not staff"""
        if self.request.user.is_staff:
            return FoodItem.objects.all()
        return FoodItem.objects.filter(meal__user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get food items by type"""
        food_type = request.query_params.get('type', None)
        queryset = self.get_queryset()
        
        if food_type:
            queryset = queryset.filter(food_type=food_type.upper())
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class BreakfastViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Breakfast meals
    """
    queryset = Breakfast.objects.all()
    serializer_class = BreakfastSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Breakfast.objects.all()
        return Breakfast.objects.filter(meal__user=self.request.user)


class LunchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Lunch meals
    """
    queryset = Lunch.objects.all()
    serializer_class = LunchSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Lunch.objects.all()
        return Lunch.objects.filter(meal__user=self.request.user)


class DinnerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Dinner meals
    """
    queryset = Dinner.objects.all()
    serializer_class = DinnerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Dinner.objects.all()
        return Dinner.objects.filter(meal__user=self.request.user)


class SnackViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Snack meals
    """
    queryset = Snack.objects.all()
    serializer_class = SnackSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Snack.objects.all()
        return Snack.objects.filter(meal__user=self.request.user)


# Web Interface Views
@login_required
def meal_list_view(request):
    """Display list of user's meals"""
    meals = Meal.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'meals/meal_list.html', {
        'meals': meals
    })
