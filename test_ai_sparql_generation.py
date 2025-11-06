"""
Test AI SPARQL generation for meal creation
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smart_Health.settings')
django.setup()

from apps.ai_service.gemini_service import GeminiAIService

# Test prompts
test_prompts = [
    "add breakfast meal pancakes with 300 calories",
    "create a breakfast called eggs with 250 calories",
    "insert lunch meal sandwich 400 calories"
]

ai_service = GeminiAIService()

if not ai_service.enabled:
    print("❌ AI service not configured!")
    print("Please set GEMINI_API_KEY in .env file")
else:
    print("✅ AI service is enabled")
    print("="*70)
    
    for prompt in test_prompts:
        print(f"\n📝 Prompt: {prompt}")
        print("-"*70)
        
        try:
            # Assuming user_id = 2 (dhia)
            sparql, error = ai_service.generate_sparql(prompt, user_id=2)
            
            if error:
                print(f"❌ Error: {error}")
            else:
                print("Generated SPARQL:")
                print(sparql)
                
                # Check if it has the required properties
                has_name = 'meal_name' in sparql or 'name' in sparql
                has_calories = 'total_calories' in sparql or 'calories' in sparql
                has_user = 'has_user' in sparql or 'User_' in sparql
                
                print(f"\n✓ Properties check:")
                print(f"  - Name property: {'✅' if has_name else '❌ MISSING'}")
                print(f"  - Calories property: {'✅' if has_calories else '❌ MISSING'}")
                print(f"  - User link: {'✅' if has_user else '❌ MISSING'}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
        
        print("="*70)
