import requests

api_key = "AIzaSyCMJQCupOKyDv_18hoT8uUb8LsNy4RsSEM"
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

response = requests.get(url)
if response.status_code == 200:
    models = response.json().get('models', [])
    print("Available models that support generateContent:")
    for model in models:
        if 'generateContent' in model.get('supportedGenerationMethods', []):
            print(f"  - {model['name']}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
