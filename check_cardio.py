"""
Check Cardio table directly
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smart_Health.settings')
django.setup()

from apps.activities.models import Activity, Cardio

print("=" * 80)
print("Cardio Records")
print("=" * 80)

cardios = Cardio.objects.all().order_by('-activity_id')
print(f"\nTotal Cardio records: {cardios.count()}\n")

for cardio in cardios:
    print(f"Cardio PK: {cardio.pk}")
    print(f"   Activity ID: {cardio.activity.activity_id}")
    print(f"   Activity Name: {cardio.activity.activity_name}")
    print(f"   Heart Rate: {cardio.heart_rate}")
    print(f"   Calories: {cardio.calories_burned}")
    print()

print("=" * 80)
print("\nChecking Activity 16 specifically:")
try:
    activity = Activity.objects.get(activity_id=16)
    print(f"Activity: {activity.activity_name}")
    print(f"Has 'cardio' attr: {hasattr(activity, 'cardio')}")
    print(f"Has 'cardio_details' attr: {hasattr(activity, 'cardio_details')}")
    if hasattr(activity, 'cardio_details'):
        print(f"Cardio: {activity.cardio_details}")
    else:
        # Try reverse lookup
        cardios_for_activity = Cardio.objects.filter(activity_id=16)
        print(f"Cardios with activity_id=16: {cardios_for_activity.count()}")
        for c in cardios_for_activity:
            print(f"  - Cardio ID {c.cardio_id}: HR={c.heart_rate}, Cal={c.calories_burned}")
except Activity.DoesNotExist:
    print("Activity 16 not found")
