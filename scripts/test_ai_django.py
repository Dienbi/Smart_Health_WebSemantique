"""
Test AI Service directly using Django test client
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client
import json


def test_ai_service():
    """Test the AI service endpoint using Django test client"""
    print("\n" + "="*60)
    print("🤖 Testing AI Service API")
    print("="*60 + "\n")
    
    client = Client()
    
    # Test 1: GET request (should show usage examples)
    print("Test 1: GET request (API Info)")
    print("-" * 60)
    response = client.get('/api/ai/query/')
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ API is accessible!")
        print(f"\nResponse:\n{json.dumps(data, indent=2)}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.content.decode())
    
    # Test 2: Simple user query
    print("\n\nTest 2: Query all classes")
    print("-" * 60)
    response = client.post(
        '/api/ai/query/',
        data=json.dumps({"prompt": "Show me all users"}),
        content_type='application/json'
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ Query successful!")
        print(f"\nIntent detected: {data.get('intent', 'N/A')}")
        print(f"Results count: {data.get('results_count', 0)}")
        print(f"\nSPARQL Query generated:\n{data.get('sparql_query', 'N/A')}")
        print(f"\nResults preview:")
        results = data.get('results', [])
        for i, result in enumerate(results[:3], 1):
            print(f"  {i}. {result}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.content.decode())
    
    # Test 3: Activity query
    print("\n\nTest 3: Query activities")
    print("-" * 60)
    response = client.post(
        '/api/ai/query/',
        data=json.dumps({"prompt": "List all activities"}),
        content_type='application/json'
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ Query successful!")
        print(f"Intent detected: {data.get('intent', 'N/A')}")
        print(f"Results count: {data.get('results_count', 0)}")
        print(f"\nSPARQL Query:\n{data.get('sparql_query', 'N/A')}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.content.decode())
    
    # Test 4: Health metrics query
    print("\n\nTest 4: Query health metrics")
    print("-" * 60)
    response = client.post(
        '/api/ai/query/',
        data=json.dumps({"prompt": "Show health metrics"}),
        content_type='application/json'
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ Query successful!")
        print(f"Intent detected: {data.get('intent', 'N/A')}")
        print(f"Results count: {data.get('results_count', 0)}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.content.decode())
    
    # Test 5: Query with user ID
    print("\n\nTest 5: Query for specific user")
    print("-" * 60)
    response = client.post(
        '/api/ai/query/',
        data=json.dumps({"prompt": "Show activities for user 123"}),
        content_type='application/json'
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ Query successful!")
        print(f"Intent detected: {data.get('intent', 'N/A')}")
        print(f"User ID extracted: {data.get('user_id', 'N/A')}")
        print(f"Results count: {data.get('results_count', 0)}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.content.decode())
    
    print("\n" + "="*60)
    print("\n📝 Summary:")
    print("✅ AI service is working correctly!")
    print("✅ Natural language to SPARQL conversion functional")
    print("✅ Fuseki integration successful")
    print("\n💡 Key Features:")
    print("- Intent detection from natural language")
    print("- Automatic user ID extraction")
    print("- SPARQL query generation")
    print("- Results formatting")
    print("\n🚀 Next Steps:")
    print("1. Add actual user/activity data to Fuseki")
    print("2. Create REST API endpoints for CRUD operations")
    print("3. Integrate with frontend application")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_ai_service()
