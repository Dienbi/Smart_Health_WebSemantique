import sys
sys.path.append('D:/OneDrive/Bureau/Web Sementique/Smart_Health_Web')
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'Smart_Health.settings'
import django
django.setup()

from apps.sparql_service.client import SparqlClient

client = SparqlClient()

# Check what meals exist
query1 = """
PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
SELECT ?meal ?type WHERE { 
    ?meal a ?type . 
    FILTER(REGEX(STR(?type), "Meal|Breakfast|Lunch|Dinner")) 
}
"""

print("All meals in database:")
results = client.execute_query(query1)
for r in results['results']['bindings']:
    print(f"  {r['meal']['value']} -> {r['type']['value']}")

# Try querying with subclasses
query2 = """
PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
SELECT ?s WHERE { 
    { ?s a sh:Breakfast } UNION 
    { ?s a sh:Lunch } UNION 
    { ?s a sh:Dinner } UNION
    { ?s a sh:Snack }
}
"""

print("\nMeals by type:")
results2 = client.execute_query(query2)
print(f"Found {len(results2['results']['bindings'])} meals")
for r in results2['results']['bindings']:
    print(f"  - {r['s']['value']}")
