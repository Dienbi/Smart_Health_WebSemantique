"""
Test sync by simulating AI meal creation via API
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smart_Health.settings')
django.setup()

from apps.ai_service.views import sync_insert_from_fuseki_to_django
from apps.sparql_service.client import SparqlClient
from apps.meals.models import Meal

# First, create a meal in Fuseki using proper SPARQL
client = SparqlClient()

meal_name = "test_waffles"
sparql_insert = f"""
PREFIX sh: <http://dhia.org/ontologies/smarthealth#>

INSERT DATA {{
  sh:Breakfast_{meal_name} a sh:Breakfast ;
    sh:name "{meal_name}" ;
    sh:calories 350 .
}}
"""

print("="*70)
print("STEP 1: Insert meal in Fuseki")
print("="*70)
print(sparql_insert)

try:
    success = client.execute_update(sparql_insert)
    print(f"✅ Fuseki INSERT successful: {success}")
except Exception as e:
    print(f"❌ Fuseki INSERT failed: {str(e)}")
    exit(1)

print("\n" + "="*70)
print("STEP 2: Run sync function (what AIQueryView does)")
print("="*70)

# Now test the sync function with user_id=2 (dhia)
user_id = 2
print(f"Calling sync_insert_from_fuseki_to_django(sparql_query, user_id={user_id})")
print("Watch the logs above for pattern matching...")

sync_result = sync_insert_from_fuseki_to_django(sparql_insert, user_id)

print(f"\nSync result: {sync_result}")

if sync_result:
    print("✅ Sync returned True - meal should be in Django")
else:
    print("❌ Sync returned False - meal NOT in Django")

print("\n" + "="*70)
print("STEP 3: Verify meal in Django")
print("="*70)

django_meals = Meal.objects.filter(meal_name=meal_name)
print(f"Found {django_meals.count()} meals with name '{meal_name}' in Django")

if django_meals.exists():
    for meal in django_meals:
        print(f"✅ {meal.meal_name} ({meal.meal_type}) - {meal.total_calories} calories")
else:
    print(f"❌ Meal '{meal_name}' NOT found in Django!")

print("="*70)
