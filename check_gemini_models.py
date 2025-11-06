"""
Check available Gemini models
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
base_url = "https://generativelanguage.googleapis.com/v1beta"

print("=" * 80)
print("Checking Available Gemini Models")
print("=" * 80)

if not api_key:
    print("❌ No API key found!")
    exit(1)

print(f"\n✅ API Key found: {api_key[:20]}...")
print(f"\nFetching available models from: {base_url}/models")

try:
    response = requests.get(
        f"{base_url}/models?key={api_key}",
        timeout=10
    )
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        models_data = response.json().get('models', [])
        print(f"\n✅ Found {len(models_data)} models\n")
        print("=" * 80)
        
        for model in models_data:
            name = model.get('name', 'Unknown').replace('models/', '')
            display_name = model.get('displayName', 'N/A')
            description = model.get('description', 'N/A')[:60]
            methods = model.get('supportedGenerationMethods', [])
            
            supports_generate = 'generateContent' in methods
            
            if supports_generate:
                print(f"✅ {name}")
                print(f"   Display: {display_name}")
                print(f"   Methods: {', '.join(methods)}")
                print(f"   Description: {description}")
                print()
        
        print("=" * 80)
        print("\nBest models to use (stable):")
        stable_models = []
        for model in models_data:
            name = model.get('name', '').replace('models/', '')
            if 'generateContent' in model.get('supportedGenerationMethods', []):
                # Skip experimental versions
                if '-exp' not in name and '2.0' not in name:
                    stable_models.append(name)
        
        for model in stable_models[:5]:
            print(f"  - {model}")
            
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Exception: {e}")
    import traceback
    print(traceback.format_exc())
