"""
Check activities in the database
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smart_Health.settings')
django.setup()

from apps.activities.models import Activity, Cardio, Musculation, Natation

print("=" * 80)
print("Activities in Django Database")
print("=" * 80)

activities = Activity.objects.all().order_by('-activity_id')
print(f"\nTotal Activities: {activities.count()}\n")

for activity in activities:
    print(f"ID: {activity.activity_id} | Name: {activity.activity_name}")
    print(f"   Description: {activity.activity_description}")
    
    # Check type
    if hasattr(activity, 'cardio'):
        print(f"   Type: CARDIO - HR: {activity.cardio.heart_rate}, Calories: {activity.cardio.calories_burned}")
    elif hasattr(activity, 'musculation'):
        print(f"   Type: MUSCULATION - Sets: {activity.musculation.sets}, Reps: {activity.musculation.repetitions}")
    elif hasattr(activity, 'natation'):
        print(f"   Type: NATATION - Distance: {activity.natation.distance}m, Style: {activity.natation.style}")
    else:
        print(f"   Type: NONE (no subtype)")
    print()

print("=" * 80)
