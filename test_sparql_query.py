"""
Script de test pour diagnostiquer l'erreur 500 avec les requêtes SPARQL
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smart_Health.settings')
django.setup()

from apps.sparql_service.client import SparqlClient
from apps.sparql_service.formatter import SparqlResultFormatter
from django.conf import settings

# Test query
test_query = """
PREFIX sh: <http://dhia.org/ontologies/smarthealth#>

SELECT ?s WHERE {
  { ?s a sh:HeartRate }
  UNION
  { ?s a sh:Cholesterol }
  UNION
  { ?s a sh:SugarLevel }
  UNION
  { ?s a sh:Oxygen }
  UNION
  { ?s a sh:Weight }
  UNION
  { ?s a sh:Height }
}
"""

print("=" * 60)
print("Test SPARQL Query Execution")
print("=" * 60)
print(f"\nFuseki Endpoint: {settings.FUSEKI_ENDPOINT}")
print(f"\nQuery:\n{test_query}\n")

try:
    # Execute query
    print("1. Executing SPARQL query...")
    client = SparqlClient()
    results = client.execute_query(test_query)
    print(f"   [OK] Query executed successfully")
    print(f"   Results type: {type(results)}")
    print(f"   Results keys: {results.keys() if isinstance(results, dict) else 'N/A'}")
    
    # Format results
    print("\n2. Formatting results...")
    formatted = SparqlResultFormatter.format_results(results)
    print(f"   [OK] Results formatted successfully")
    print(f"   Formatted type: {type(formatted)}")
    print(f"   Formatted length: {len(formatted)}")
    print(f"   Formatted content: {formatted}")
    
    # Try to serialize
    print("\n3. Testing JSON serialization...")
    import json
    json_str = json.dumps({
        'success': True,
        'results_count': len(formatted),
        'results': formatted
    })
    print(f"   [OK] JSON serialization successful")
    print(f"   JSON length: {len(json_str)} characters")
    
    print("\n" + "=" * 60)
    print("[OK] All tests passed!")
    print("=" * 60)
    
except Exception as e:
    import traceback
    print(f"\n[ERROR] Error occurred:")
    print(f"   Error type: {type(e).__name__}")
    print(f"   Error message: {str(e)}")
    print(f"\n   Traceback:")
    print(traceback.format_exc())
    
    print("\n" + "=" * 60)
    print("[ERROR] Test failed!")
    print("=" * 60)

