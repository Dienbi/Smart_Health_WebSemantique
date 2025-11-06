"""
Quick test to check Fuseki connection and sync functionality
"""
import sys
import os
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smart_Health.settings')
django.setup()

from apps.sparql_service.client import SparqlClient
from apps.users.models import User

print("=" * 60)
print("FUSEKI & SYNC TEST")
print("=" * 60)

# Test 1: Check Fuseki connection
print("\n1. Testing Fuseki connection...")
try:
    client = SparqlClient()
    test_query = """
    PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
    SELECT (COUNT(*) as ?count)
    WHERE {
        ?s ?p ?o
    }
    """
    result = client.execute_query(test_query)
    count = result['results']['bindings'][0]['count']['value']
    print(f"   ✅ Fuseki is running!")
    print(f"   ✅ Triple count in Fuseki: {count}")
except Exception as e:
    print(f"   ❌ Fuseki connection failed: {str(e)}")
    print(f"   💡 Make sure Fuseki is running on http://localhost:3030")
    sys.exit(1)

# Test 2: Check users in Django
print("\n2. Checking Django users...")
try:
    users = User.objects.all()
    print(f"   ✅ Found {users.count()} user(s) in Django:")
    for user in users:
        print(f"      - {user.username} (ID: {user.user_id})")
except Exception as e:
    print(f"   ❌ Error checking users: {str(e)}")

# Test 3: Test AI meal creation with sync
print("\n3. Testing AI meal creation with sync...")
try:
    from apps.ai_service.views import sync_insert_from_fuseki_to_django
    
    # Sample SPARQL query that AI would generate
    test_sparql = """
    PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
    
    INSERT DATA {
        sh:Meal_Test a sh:Breakfast ;
            sh:meal_name "Test Oatmeal" ;
            sh:total_calories 300 .
    }
    """
    
    print(f"   Testing with SPARQL:\n{test_sparql}")
    
    user = User.objects.first()
    if user:
        result = sync_insert_from_fuseki_to_django(test_sparql, user.user_id)
        if result:
            print(f"   ✅ Sync function returned True - meal should be created")
            
            # Verify in Django
            from apps.meals.models import Meal
            meal = Meal.objects.filter(meal_name="Test Oatmeal").first()
            if meal:
                print(f"   ✅ Verified: Meal found in Django database!")
                print(f"      - Name: {meal.meal_name}")
                print(f"      - Type: {meal.meal_type}")
                print(f"      - Calories: {meal.total_calories}")
                print(f"      - ID: {meal.meal_id}")
                
                # Clean up test data
                meal.delete()
                print(f"   🧹 Test meal deleted")
            else:
                print(f"   ❌ Meal NOT found in Django database - sync failed!")
        else:
            print(f"   ❌ Sync function returned False - check logs")
    else:
        print(f"   ❌ No users found - cannot test")
        
except Exception as e:
    import traceback
    print(f"   ❌ Error during sync test: {str(e)}")
    print(f"   Traceback:\n{traceback.format_exc()}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
