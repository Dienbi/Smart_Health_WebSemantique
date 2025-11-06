"""
Test syncing existing pancakes meal from Fuseki to Django
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smart_Health.settings')
django.setup()

from apps.ai_service.views import sync_insert_from_fuseki_to_django
from apps.meals.models import Meal

# Simulate the SPARQL that was used to create pancakes
# Based on your earlier message, the AI generates: sh:Breakfast_pancakes

# Since we don't know the exact SPARQL, let's test with a typical AI-generated format
sparql_pancakes = """
PREFIX sh: <http://dhia.org/ontologies/smarthealth#>

INSERT DATA {
  sh:Breakfast_pancakes a sh:Breakfast ;
    sh:name "pancakes" ;
    sh:calories 400 .
}
"""

print("="*70)
print("SYNCING PANCAKES FROM FUSEKI TO DJANGO")
print("="*70)
print(f"SPARQL:\n{sparql_pancakes}")
print("="*70)

# Test with user_id=2 (dhia - based on earlier tests showing 3 users)
user_id = 2

print(f"\nCalling sync_insert_from_fuseki_to_django(sparql, user_id={user_id})...")
print("(Check output above for pattern matching details)")

result = sync_insert_from_fuseki_to_django(sparql_pancakes, user_id)

print(f"\n{'='*70}")
print(f"Sync Result: {result}")

if result:
    print("✅ Sync succeeded - checking Django...")
    
    pancakes = Meal.objects.filter(meal_name__icontains="pancakes")
    print(f"\nMeals matching 'pancakes': {pancakes.count()}")
    
    for meal in pancakes:
        print(f"  - {meal.meal_name} ({meal.meal_type}) - {meal.total_calories} cal [ID: {meal.meal_id}]")
else:
    print("❌ Sync failed - meal NOT created in Django")
    print("\nChecking if it exists anyway...")
    
    pancakes = Meal.objects.filter(meal_name__icontains="pancakes")
    if pancakes.exists():
        print(f"🤔 Found {pancakes.count()} pancakes meals in Django (created earlier?)")
        for meal in pancakes:
            print(f"  - {meal.meal_name} ({meal.meal_type}) - {meal.total_calories} cal")
    else:
        print("❌ No pancakes meals in Django database")

print("="*70)
