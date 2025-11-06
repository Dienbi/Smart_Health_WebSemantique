"""Check which users own the meals"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smart_Health.settings')
django.setup()

from apps.meals.models import Meal
from apps.users.models import User

print("\n" + "="*60)
print("MEALS AND THEIR USERS")
print("="*60)

meals = Meal.objects.all()
for meal in meals:
    if meal.user:
        print(f"  {meal.meal_name} ({meal.meal_type}) → User: {meal.user.username} (ID: {meal.user.user_id})")
    else:
        print(f"  {meal.meal_name} ({meal.meal_type}) → NO USER ASSIGNED!")

print("\n" + "="*60)
print("ALL USERS IN SYSTEM")
print("="*60)

users = User.objects.all()
for user in users:
    meal_count = Meal.objects.filter(user=user).count()
    print(f"  {user.username} (ID: {user.user_id}) - {meal_count} meals")

print("="*60 + "\n")
