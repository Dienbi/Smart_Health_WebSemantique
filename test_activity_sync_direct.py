"""
Test activity sync directly without using AI (bypass quota issue)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smart_Health.settings')
django.setup()

from apps.ai_service.views import sync_insert_from_fuseki_to_django
from apps.sparql_service.sparql_client import SparqlClient

# Hardcoded SPARQL queries (what the AI would generate)
test_activities = [
    {
        'name': 'jogging',
        'type': 'Cardio',
        'sparql': 'PREFIX sh: <http://dhia.org/ontologies/smarthealth#>\n\nINSERT DATA { sh:Cardio_jogging a sh:Cardio ; sh:activity_name "jogging" }'
    },
    {
        'name': 'bench press',
        'type': 'Musculation',
        'sparql': 'PREFIX sh: <http://dhia.org/ontologies/smarthealth#>\n\nINSERT DATA { sh:Musculation_benchpress a sh:Musculation ; sh:activity_name "bench press" }'
    },
    {
        'name': 'swimming',
        'type': 'Natation',
        'sparql': 'PREFIX sh: <http://dhia.org/ontologies/smarthealth#>\n\nINSERT DATA { sh:Natation_swimming a sh:Natation ; sh:activity_name "swimming" }'
    }
]

print("=" * 80)
print("Testing Activity Sync (Direct - No AI)")
print("=" * 80)

client = SparqlClient()
user_id = 3  # Test as assil

for test in test_activities:
    print(f"\n{'=' * 80}")
    print(f"Test: Create {test['type']} - {test['name']}")
    print("-" * 80)
    print(f"SPARQL:\n{test['sparql']}")
    print("-" * 80)
    
    # Execute SPARQL in Fuseki
    print("📝 Executing SPARQL in Fuseki...")
    success = client.execute_update(test['sparql'])
    
    if success:
        print("✅ SPARQL executed in Fuseki")
        
        # Sync to Django
        print("🔄 Syncing to Django...")
        sync_result = sync_insert_from_fuseki_to_django(test['sparql'], user_id)
        
        if sync_result:
            print(f"✅ Successfully synced to Django!")
        else:
            print(f"❌ Sync to Django failed")
    else:
        print("❌ Failed to execute SPARQL in Fuseki")

print(f"\n{'=' * 80}")
print("Checking Django database...")
print("-" * 80)

from apps.activities.models import Activity, Cardio, Musculation, Natation

activities = Activity.objects.all()
print(f"\nTotal Activities in Django: {activities.count()}")
for activity in activities:
    print(f"  - {activity.activity_name} (ID: {activity.activity_id})")
    
    # Check type details
    if hasattr(activity, 'cardio'):
        print(f"    Type: Cardio (HR: {activity.cardio.heart_rate}, Calories: {activity.cardio.calories_burned})")
    elif hasattr(activity, 'musculation'):
        print(f"    Type: Musculation (Sets: {activity.musculation.sets}, Reps: {activity.musculation.repetitions}, Weight: {activity.musculation.weight}kg)")
    elif hasattr(activity, 'natation'):
        print(f"    Type: Natation (Distance: {activity.natation.distance}m, Style: {activity.natation.style})")

print(f"\n{'=' * 80}")
print("Test completed!")
print("=" * 80)
