"""
Test Fuseki connection and query data
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smart_Health.settings')
django.setup()

from apps.sparql_service.client import SparqlClient


def test_connection():
    """Test basic connection to Fuseki"""
    print("\n" + "="*60)
    print("🔍 Testing Fuseki Connection")
    print("="*60 + "\n")
    
    client = SparqlClient()
    
    # Test 1: Count all triples
    print("Test 1: Counting all triples...")
    query1 = """
    SELECT (COUNT(*) as ?count)
    WHERE {
        ?s ?p ?o
    }
    """
    
    try:
        results = client.execute_query(query1)
        print(f"✅ Connection successful!")
        print(f"Results: {results}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return
    
    # Test 2: Get any 10 triples
    print("\n\nTest 2: Getting first 10 triples...")
    query2 = """
    SELECT ?s ?p ?o
    WHERE {
        ?s ?p ?o
    }
    LIMIT 10
    """
    
    try:
        results = client.execute_query(query2)
        print(f"✅ Query successful!")
        if results and 'results' in results and 'bindings' in results['results']:
            bindings = results['results']['bindings']
            print(f"Number of results: {len(bindings)}")
            if len(bindings) > 0:
                print("\nFirst few triples:")
                for i, binding in enumerate(bindings[:5], 1):
                    s = binding.get('s', {}).get('value', 'N/A')
                    p = binding.get('p', {}).get('value', 'N/A')
                    o = binding.get('o', {}).get('value', 'N/A')
                    print(f"{i}. {s} -> {p} -> {o}")
            else:
                print("⚠️  No triples found in the database!")
                print("\nPossible reasons:")
                print("1. The ontology file was not uploaded correctly")
                print("2. The dataset name is incorrect")
                print("3. The upload went to a different graph")
        else:
            print("⚠️  Unexpected response format")
            print(results)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 3: Check for classes
    print("\n\nTest 3: Looking for OWL/RDFS classes...")
    query3 = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT DISTINCT ?class ?type
    WHERE {
        {
            ?class a owl:Class
            BIND("owl:Class" as ?type)
        }
        UNION
        {
            ?class a rdfs:Class
            BIND("rdfs:Class" as ?type)
        }
    }
    LIMIT 20
    """
    
    try:
        results = client.execute_query(query3)
        if results and 'results' in results and 'bindings' in results['results']:
            bindings = results['results']['bindings']
            print(f"✅ Found {len(bindings)} classes")
            if len(bindings) > 0:
                print("\nClasses found:")
                for binding in bindings[:10]:
                    class_uri = binding.get('class', {}).get('value', 'N/A')
                    class_type = binding.get('type', {}).get('value', 'N/A')
                    print(f"  - {class_uri} ({class_type})")
            else:
                print("⚠️  No classes found!")
        else:
            print("⚠️  Unexpected response format")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 4: Check for SmartHealth namespace
    print("\n\nTest 4: Looking for SmartHealth ontology data...")
    query4 = """
    SELECT ?s ?p ?o
    WHERE {
        ?s ?p ?o
        FILTER(STRSTARTS(STR(?s), "http://dhia.org/ontologies/smarthealth#"))
    }
    LIMIT 10
    """
    
    try:
        results = client.execute_query(query4)
        if results and 'results' in results and 'bindings' in results['results']:
            bindings = results['results']['bindings']
            print(f"✅ Found {len(bindings)} triples with SmartHealth namespace")
            if len(bindings) > 0:
                print("\nSmartHealth data found:")
                for i, binding in enumerate(bindings[:5], 1):
                    s = binding.get('s', {}).get('value', 'N/A')
                    p = binding.get('p', {}).get('value', 'N/A')
                    o = binding.get('o', {}).get('value', 'N/A')
                    print(f"{i}. {s}")
                    print(f"   {p} -> {o}\n")
            else:
                print("⚠️  No SmartHealth data found!")
                print("\n📝 This means the TTL file wasn't uploaded or went to a different graph.")
                print("\nTry uploading again using:")
                print("  1. Fuseki web interface: http://localhost:3030/#/dataset/smarthealth/upload")
                print("  2. Make sure to select 'default graph'")
                print("  3. Or run: python scripts\\import_ontology.py")
        else:
            print("⚠️  Unexpected response format")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    test_connection()
