"""
Quick test to check if everything is configured properly
"""
import os
import sys

print("="*60)
print("Testing Smart Health Setup")
print("="*60)

# Test 1: Check .env file
print("\n1. Checking .env file...")
from dotenv import load_dotenv
load_dotenv()

gemini_key = os.getenv('GEMINI_API_KEY')
fuseki_endpoint = os.getenv('FUSEKI_ENDPOINT', 'http://localhost:3030/smarthealth/sparql')

if gemini_key:
    print(f"   ✅ GEMINI_API_KEY found ({gemini_key[:10]}...)")
else:
    print("   ❌ GEMINI_API_KEY not found in .env")

print(f"   📍 Fuseki endpoint: {fuseki_endpoint}")

# Test 2: Check Fuseki connection
print("\n2. Testing Fuseki connection...")
try:
    import requests
    response = requests.get(fuseki_endpoint.replace('/sparql', '/query?query=SELECT+*+WHERE+{+?s+?p+?o+}+LIMIT+1'), timeout=5)
    if response.status_code == 200:
        print("   ✅ Fuseki is running and responding")
    else:
        print(f"   ⚠️ Fuseki responded with status {response.status_code}")
except requests.exceptions.ConnectionError:
    print("   ❌ Cannot connect to Fuseki - Is it running?")
    print("   💡 Start Fuseki with: cd C:\\apache-jena-fuseki-5.2.0 && .\\fuseki-server.bat")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Check Gemini AI
print("\n3. Testing Gemini AI...")
try:
    from apps.ai_service.gemini_service import GeminiAIService
    ai = GeminiAIService()
    if ai.enabled:
        print(f"   ✅ Gemini AI enabled with model: {ai.model_name}")
    else:
        print("   ❌ Gemini AI not enabled - check API key")
except Exception as e:
    print(f"   ❌ Error loading AI service: {e}")

# Test 4: Django settings
print("\n4. Checking Django settings...")
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smart_Health.settings')
    import django
    django.setup()
    from django.conf import settings as django_settings
    print(f"   ✅ Django configured with DEBUG={django_settings.DEBUG}")
    print(f"   📍 Database: {django_settings.DATABASES['default']['NAME']}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*60)
print("Test Complete!")
print("="*60)
