"""
Test script to verify all API endpoints are accessible
Run this after starting the Django server
"""
import requests
from pprint import pprint

BASE_URL = "http://127.0.0.1:8000/api"

# Note: You need to authenticate first to get a token
# For now, this script just tests if endpoints are accessible

def test_endpoint(url, name):
    """Test if an endpoint is accessible"""
    try:
        response = requests.get(url)
        status = "✅" if response.status_code in [200, 401, 403] else "❌"
        print(f"{status} {name}: {response.status_code}")
        return response.status_code
    except Exception as e:
        print(f"❌ {name}: Error - {str(e)}")
        return None


def main():
    print("=" * 60)
    print("Testing Smart Health Web API Endpoints")
    print("=" * 60)
    
    endpoints = {
        "Activities": [
            f"{BASE_URL}/activities/activities/",
            f"{BASE_URL}/activities/logs/",
            f"{BASE_URL}/activities/cardio/",
            f"{BASE_URL}/activities/musculation/",
            f"{BASE_URL}/activities/natation/",
        ],
        "Habits": [
            f"{BASE_URL}/habits/habits/",
            f"{BASE_URL}/habits/logs/",
            f"{BASE_URL}/habits/reading/",
            f"{BASE_URL}/habits/cooking/",
            f"{BASE_URL}/habits/drawing/",
            f"{BASE_URL}/habits/journaling/",
        ],
        "Meals": [
            f"{BASE_URL}/meals/meals/",
            f"{BASE_URL}/meals/food-items/",
            f"{BASE_URL}/meals/breakfast/",
            f"{BASE_URL}/meals/lunch/",
            f"{BASE_URL}/meals/dinner/",
            f"{BASE_URL}/meals/snack/",
        ],
        "Health Records": [
            f"{BASE_URL}/health-records/records/",
            f"{BASE_URL}/health-records/metrics/",
            f"{BASE_URL}/health-records/student-records/",
            f"{BASE_URL}/health-records/teacher-records/",
        ],
        "Défis": [
            f"{BASE_URL}/defis/defis/",
            f"{BASE_URL}/defis/participations/",
        ],
        "AI Service": [
            f"{BASE_URL}/ai/query/",
        ],
    }
    
    total_endpoints = 0
    accessible_endpoints = 0
    
    for category, urls in endpoints.items():
        print(f"\n{category}:")
        print("-" * 60)
        for url in urls:
            status = test_endpoint(url, url.replace(BASE_URL, ""))
            total_endpoints += 1
            if status in [200, 401, 403]:  # 401/403 means endpoint exists but needs auth
                accessible_endpoints += 1
    
    print("\n" + "=" * 60)
    print(f"Summary: {accessible_endpoints}/{total_endpoints} endpoints accessible")
    print("=" * 60)
    print("\nNote: 401/403 status codes are expected (authentication required)")
    print("To test authenticated endpoints, you need to:")
    print("1. Create a superuser: python manage.py createsuperuser")
    print("2. Get an authentication token")
    print("3. Include the token in your requests")


if __name__ == "__main__":
    main()
