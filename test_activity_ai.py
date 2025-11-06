"""
Test script to see what SPARQL the AI generates for activity creation
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smart_Health.settings')
django.setup()

from apps.ai_service.gemini_service import GeminiAIService

# Test prompts
test_prompts = [
    "create activity jogging",
    "add activity running",
    "create activity bench press",
    "add activity swimming"
]

ai_service = GeminiAIService()

print("=" * 80)
print("Testing AI SPARQL Generation for Activities")
print("=" * 80)

for prompt in test_prompts:
    print(f"\n{'=' * 80}")
    print(f"Prompt: {prompt}")
    print("-" * 80)
    
    sparql_query, error = ai_service.generate_sparql(prompt, user_id=3)
    
    if error:
        print(f"❌ Error: {error}")
    else:
        print(f"✅ Generated SPARQL:")
        print(sparql_query)
    
    print("-" * 80)

print(f"\n{'=' * 80}")
print("Test completed!")
print("=" * 80)
