from django.contrib import admin
from .models import (
    Meal, FoodItem, Calories, Protein, Carbs, Fiber, Sugar,
    Breakfast, Lunch, Dinner, Snack
)


class FoodItemInline(admin.TabularInline):
    model = FoodItem
    extra = 1


class CaloriesInline(admin.StackedInline):
    model = Calories
    extra = 0


class ProteinInline(admin.StackedInline):
    model = Protein
    extra = 0


class CarbsInline(admin.StackedInline):
    model = Carbs
    extra = 0


class FiberInline(admin.StackedInline):
    model = Fiber
    extra = 0


class SugarInline(admin.StackedInline):
    model = Sugar
    extra = 0


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('meal_id', 'user', 'meal_name', 'meal_type', 'total_calories', 'meal_date')
    search_fields = ('user__username', 'meal_name')
    list_filter = ('meal_type', 'meal_date', 'created_at')
    inlines = [FoodItemInline]
    date_hierarchy = 'meal_date'


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('food_item_id', 'meal', 'food_item_name', 'food_type')
    search_fields = ('food_item_name', 'meal__meal_name')
    list_filter = ('food_type',)
    inlines = [CaloriesInline, ProteinInline, CarbsInline, FiberInline, SugarInline]


@admin.register(Breakfast)
class BreakfastAdmin(admin.ModelAdmin):
    list_display = ('meal', 'breakfast_score')
    search_fields = ('meal__meal_name',)


@admin.register(Lunch)
class LunchAdmin(admin.ModelAdmin):
    list_display = ('meal', 'lunch_score')
    search_fields = ('meal__meal_name',)


@admin.register(Dinner)
class DinnerAdmin(admin.ModelAdmin):
    list_display = ('meal', 'dinner_score')
    search_fields = ('meal__meal_name',)


@admin.register(Snack)
class SnackAdmin(admin.ModelAdmin):
    list_display = ('meal', 'snack_score')
    search_fields = ('meal__meal_name',)
