"""
Simple test to verify activities are working
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smart_Health.settings')
django.setup()

from apps.activities.models import Activity, ActivityLog, Cardio, Musculation, Natation
from apps.users.models import User

print("=" * 80)
print("🎯 ACTIVITY SYSTEM TEST")
print("=" * 80)

# 1. Check Activities (definitions)
activities = Activity.objects.all()
print(f"\n✅ Total Activities (definitions): {activities.count()}")
print("\nRecent activities:")
for activity in activities.order_by('-activity_id')[:5]:
    activity_type = "Unknown"
    if hasattr(activity, 'cardio_details'):
        activity_type = f"Cardio (HR:{activity.cardio_details.heart_rate}, Cal:{activity.cardio_details.calories_burned})"
    elif hasattr(activity, 'musculation_details'):
        activity_type = f"Musculation (Sets:{activity.musculation_details.sets}x{activity.musculation_details.repetitions})"
    elif hasattr(activity, 'natation_details'):
        activity_type = f"Natation ({activity.natation_details.distance}m)"
    
    print(f"  • ID {activity.activity_id}: {activity.activity_name} - {activity_type}")

# 2. Check ActivityLogs (user instances)
logs = ActivityLog.objects.all()
print(f"\n📋 Total ActivityLogs (user instances): {logs.count()}")
if logs.count() > 0:
    print("\nRecent logs:")
    for log in logs.order_by('-activity_log_id')[:5]:
        print(f"  • {log.user.username} did '{log.activity.activity_name}' on {log.date.strftime('%Y-%m-%d %H:%M')}")
else:
    print("  ℹ️  No activity logs yet - these are created when users log their workouts")

print("\n" + "=" * 80)
print("🧪 TEST RESULTS:")
print("=" * 80)
print(f"✅ Activity Creation: {'WORKING' if activities.count() > 0 else 'FAILED'}")
print(f"✅ Activity Types: {'WORKING' if activities.filter(cardio_details__isnull=False).count() > 0 else 'FAILED'}")
print(f"ℹ️  ActivityLogs: {logs.count()} (These show in the interface)")
print("\n💡 TIP: The '/activities/' page shows ActivityLogs, not Activity definitions.")
print("   To see your created activities:")
print("   1. Visit http://127.0.0.1:8000/admin/ → Activities")
print("   2. Or ask the AI: 'show me all activities'")
print("=" * 80)
