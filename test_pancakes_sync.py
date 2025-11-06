"""
Test script to check pancakes meal sync
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smart_Health.settings')
django.setup()

from apps.sparql_service.client import SparqlClient
from apps.sparql_service.formatter import SparqlResultFormatter
from apps.meals.models import Meal
from apps.users.models import User

def check_fuseki_meals():
    """Check all meals in Fuseki"""
    client = SparqlClient()
    query = """
    PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
    
    SELECT ?meal ?name ?calories ?type
    WHERE {
        ?meal a ?type .
        FILTER (?type IN (sh:Breakfast, sh:Lunch, sh:Dinner, sh:Snack))
        OPTIONAL { ?meal sh:meal_name ?name }
        OPTIONAL { ?meal sh:name ?name }
        OPTIONAL { ?meal sh:total_calories ?calories }
        OPTIONAL { ?meal sh:calories ?calories }
    }
    """
    
    raw_results = client.execute_query(query)
    results = SparqlResultFormatter.format_results(raw_results)
    
    print("\n🔍 Meals in Fuseki:")
    print(f"Found {len(results)} meals")
    
    for i, result in enumerate(results, 1):
        meal_uri = result.get('meal', 'Unknown')
        meal_name = result.get('name', 'NO NAME')
        meal_calories = result.get('calories', 'NO CALORIES')
        meal_type = result.get('type', 'Unknown')
        
        print(f"\n  {i}. {meal_uri}")
        print(f"     Name: {meal_name}")
        print(f"     Calories: {meal_calories}")
        print(f"     Type: {meal_type}")
    
    return results

def check_django_meals():
    """Check all meals in Django"""
    meals = Meal.objects.all()
    print(f"\n📊 Meals in Django: {meals.count()} meals")
    
    for meal in meals:
        print(f"  - {meal.meal_name} ({meal.meal_type}) - {meal.total_calories} calories")
    
    return meals

def test_pancakes_query():
    """Test query for pancakes specifically"""
    client = SparqlClient()
    query = """
    PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
    
    SELECT ?meal ?prop ?value
    WHERE {
        ?meal ?prop ?value .
        FILTER (CONTAINS(STR(?meal), "pancakes") || CONTAINS(STR(?meal), "Breakfast_pancakes"))
    }
    """
    
    raw_results = client.execute_query(query)
    results = SparqlResultFormatter.format_results(raw_results)
    
    print(f"\n🥞 Pancakes meal details ({len(results)} properties):")
    
    for result in results:
        prop = result.get('prop', 'Unknown')
        value = result.get('value', 'Unknown')
        print(f"  {prop} = {value}")
    
    return results

if __name__ == "__main__":
    print("="*70)
    print("MEAL SYNCHRONIZATION TEST - PANCAKES")
    print("="*70)
    
    # Check Fuseki meals
    fuseki_meals = check_fuseki_meals()
    
    # Check Django meals
    django_meals = check_django_meals()
    
    # Check pancakes specifically
    pancakes_details = test_pancakes_query()
    
    print("\n" + "="*70)
    print(f"SUMMARY:")
    print(f"  Fuseki: {len(fuseki_meals)} meals")
    print(f"  Django: {django_meals.count()} meals")
    print(f"  Missing: {len(fuseki_meals) - django_meals.count()} meals not synced")
    print("="*70)
