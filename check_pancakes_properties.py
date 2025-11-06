"""
Check exact SPARQL properties for pancakes
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smart_Health.settings')
django.setup()

from apps.sparql_service.client import SparqlClient
from apps.sparql_service.formatter import SparqlResultFormatter

client = SparqlClient()

# Get ALL properties for Breakfast_pancakes
query = """
PREFIX sh: <http://dhia.org/ontologies/smarthealth#>

SELECT ?prop ?value
WHERE {
    sh:Breakfast_pancakes ?prop ?value .
}
"""

raw_results = client.execute_query(query)
results = SparqlResultFormatter.format_results(raw_results)

print("🥞 ALL PROPERTIES for Breakfast_pancakes:")
print("="*60)
for result in results:
    prop = result.get('prop', 'Unknown')
    value = result.get('value', 'Unknown')
    # Shorten URIs for readability
    if prop.startswith('http://www.w3.org/'):
        prop_short = prop.split('#')[-1] if '#' in prop else prop.split('/')[-1]
    elif prop.startswith('http://dhia.org/'):
        prop_short = 'sh:' + prop.split('#')[-1]
    else:
        prop_short = prop
    print(f"  {prop_short} = {value}")

print("\n" + "="*60)
print("Looking for these expected properties:")
print("  - sh:meal_name or sh:name")
print("  - sh:total_calories or sh:calories")
print("  - sh:has_user (link to user)")
print("="*60)
