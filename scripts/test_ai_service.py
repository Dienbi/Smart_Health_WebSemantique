"""
Test AI Service API endpoint
"""

import requests
import json


def test_ai_service():
    """Test the AI service endpoint"""
    print("\n" + "="*60)
    print("🤖 Testing AI Service API")
    print("="*60 + "\n")
    
    base_url = "http://127.0.0.1:8000/api/ai/query/"
    
    # Test 1: GET request (should show usage examples)
    print("Test 1: GET request (API Info)")
    print("-" * 60)
    try:
        response = requests.get(base_url)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ API is accessible!")
            print(f"\nResponse:\n{json.dumps(data, indent=2)}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Connection Error: {str(e)}")
        print("\nMake sure Django server is running!")
        return
    
    # Test 2: Simple user query
    print("\n\nTest 2: Query users")
    print("-" * 60)
    test_query_1 = {
        "prompt": "Show me all users"
    }
    try:
        response = requests.post(base_url, json=test_query_1)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Query successful!")
            print(f"\nResponse:\n{json.dumps(data, indent=2)}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 3: Activity query
    print("\n\nTest 3: Query activities")
    print("-" * 60)
    test_query_2 = {
        "prompt": "List all activities"
    }
    try:
        response = requests.post(base_url, json=test_query_2)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Query successful!")
            print(f"\nResponse:\n{json.dumps(data, indent=2)}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 4: Health metrics query
    print("\n\nTest 4: Query health metrics")
    print("-" * 60)
    test_query_3 = {
        "prompt": "Show health metrics"
    }
    try:
        response = requests.post(base_url, json=test_query_3)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Query successful!")
            print(f"\nResponse:\n{json.dumps(data, indent=2)}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 5: Query with user ID
    print("\n\nTest 5: Query for specific user")
    print("-" * 60)
    test_query_4 = {
        "prompt": "Show activities for user 123"
    }
    try:
        response = requests.post(base_url, json=test_query_4)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Query successful!")
            print(f"\nResponse:\n{json.dumps(data, indent=2)}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 6: Meals query
    print("\n\nTest 6: Query meals")
    print("-" * 60)
    test_query_5 = {
        "prompt": "List all meals"
    }
    try:
        response = requests.post(base_url, json=test_query_5)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Query successful!")
            print(f"\nResponse:\n{json.dumps(data, indent=2)}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n" + "="*60)
    print("\n📝 Summary:")
    print("- The AI service converts natural language to SPARQL")
    print("- Results come from your ontology in Fuseki")
    print("- Currently showing ontology structure (no user data yet)")
    print("\n💡 Next steps:")
    print("1. Add actual user/activity data to Fuseki")
    print("2. Create REST API endpoints for CRUD operations")
    print("3. Integrate with your frontend")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_ai_service()
