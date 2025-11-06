"""
Manually test SPARQL INSERT with proper properties
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smart_Health.settings')
django.setup()

from apps.sparql_service.client import SparqlClient
from apps.sparql_service.formatter import SparqlResultFormatter

client = SparqlClient()

# Test 1: Insert a complete meal with all properties (like coffee example)
print("TEST 1: Insert complete meal (like AI generated)")
print("="*70)

insert_query1 = """
PREFIX sh: <http://dhia.org/ontologies/smarthealth#>

INSERT DATA {
  sh:Meal_test_complete a sh:Breakfast ;
    sh:calories 500 ;
    sh:name "test complete" .
}
"""

print("Executing:")
print(insert_query1)

try:
    success = client.execute_update(insert_query1)
    print(f"✅ INSERT successful: {success}")
except Exception as e:
    print(f"❌ INSERT failed: {str(e)}")

# Check if it was stored properly
print("\nChecking stored properties...")
check_query = """
PREFIX sh: <http://dhia.org/ontologies/smarthealth#>

SELECT ?prop ?value
WHERE {
    sh:Meal_test_complete ?prop ?value .
}
"""

raw_results = client.execute_query(check_query)
results = SparqlResultFormatter.format_results(raw_results)

print(f"Found {len(results)} properties:")
for result in results:
    prop = result.get('prop', 'Unknown')
    value = result.get('value', 'Unknown')
    prop_short = prop.split('#')[-1] if '#' in prop else prop.split('/')[-1]
    print(f"  {prop_short} = {value}")

print("\n" + "="*70)

# Test 2: Insert with proper property names (meal_name, total_calories)
print("\nTEST 2: Insert with proper property names")
print("="*70)

insert_query2 = """
PREFIX sh: <http://dhia.org/ontologies/smarthealth#>

INSERT DATA {
  sh:Meal_test_proper a sh:Breakfast ;
    sh:meal_name "test proper" ;
    sh:total_calories 600 ;
    sh:has_user sh:User_2 .
}
"""

print("Executing:")
print(insert_query2)

try:
    success = client.execute_update(insert_query2)
    print(f"✅ INSERT successful: {success}")
except Exception as e:
    print(f"❌ INSERT failed: {str(e)}")

# Check if it was stored properly
print("\nChecking stored properties...")
check_query2 = """
PREFIX sh: <http://dhia.org/ontologies/smarthealth#>

SELECT ?prop ?value
WHERE {
    sh:Meal_test_proper ?prop ?value .
}
"""

raw_results2 = client.execute_query(check_query2)
results2 = SparqlResultFormatter.format_results(raw_results2)

print(f"Found {len(results2)} properties:")
for result in results2:
    prop = result.get('prop', 'Unknown')
    value = result.get('value', 'Unknown')
    prop_short = prop.split('#')[-1] if '#' in prop else prop.split('/')[-1]
    print(f"  {prop_short} = {value}")

print("\n" + "="*70)
print("CONCLUSION:")
print("  Test 1 uses: sh:name + sh:calories (AI style)")
print("  Test 2 uses: sh:meal_name + sh:total_calories (expected style)")
print("  Both should sync to Django if properties are stored correctly")
print("="*70)
