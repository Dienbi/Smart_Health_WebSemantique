from rest_framework import serializers
from .models import (
    Meal, FoodItem, Calories, Protein, Carbs, Fiber, Sugar,
    Breakfast, Lunch, Dinner, Snack
)


class CaloriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calories
        fields = '__all__'


class ProteinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Protein
        fields = '__all__'


class CarbsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carbs
        fields = '__all__'


class FiberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fiber
        fields = '__all__'


class SugarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sugar
        fields = '__all__'


class FoodItemSerializer(serializers.ModelSerializer):
    calories = CaloriesSerializer(read_only=True)
    protein = ProteinSerializer(read_only=True)
    carbs = CarbsSerializer(read_only=True)
    fiber = FiberSerializer(read_only=True)
    sugar = SugarSerializer(read_only=True)
    
    class Meta:
        model = FoodItem
        fields = '__all__'
        read_only_fields = ('food_item_id',)


class MealSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    food_items = FoodItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Meal
        fields = '__all__'
        read_only_fields = ('meal_id',)


class BreakfastSerializer(serializers.ModelSerializer):
    meal = MealSerializer(read_only=True)
    
    class Meta:
        model = Breakfast
        fields = '__all__'


class LunchSerializer(serializers.ModelSerializer):
    meal = MealSerializer(read_only=True)
    
    class Meta:
        model = Lunch
        fields = '__all__'


class DinnerSerializer(serializers.ModelSerializer):
    meal = MealSerializer(read_only=True)
    
    class Meta:
        model = Dinner
        fields = '__all__'


class SnackSerializer(serializers.ModelSerializer):
    meal = MealSerializer(read_only=True)
    
    class Meta:
        model = Snack
        fields = '__all__'
