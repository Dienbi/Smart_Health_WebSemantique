"""Quick test to check meals in Django database"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smart_Health.settings')
django.setup()

from apps.meals.models import Meal

meals = Meal.objects.all()
print(f"\n{'='*60}")
print(f"MEALS IN DJANGO DATABASE: {meals.count()} meals")
print(f"{'='*60}")

if meals.exists():
    for meal in meals:
        print(f"  • {meal.meal_name} ({meal.meal_type}) - {meal.total_calories} cal [ID: {meal.meal_id}]")
else:
    print("  No meals found in Django database!")

print(f"{'='*60}\n")
