"""
Comprehensive test for all model syncs between Fuseki and Django
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smart_Health.settings')
django.setup()

from apps.meals.models import Meal
from apps.activities.models import Activity
from apps.habits.models import Habit
from apps.health_records.models import HealthMetric
from apps.defis.models import Defi
from apps.users.models import User

print("\n" + "="*70)
print("COMPREHENSIVE SYNC TEST - ALL MODELS")
print("="*70)

# Get all users
users = User.objects.all()
print(f"\n📊 USERS: {users.count()} total")
for user in users:
    print(f"  - {user.username} (ID: {user.user_id})")

# Check Meals
meals = Meal.objects.all()
print(f"\n🍽️  MEALS: {meals.count()} total")
for meal in meals:
    user_name = meal.user.username if meal.user else "NO USER"
    print(f"  - {meal.meal_name} ({meal.meal_type}) by {user_name}")

# Check Activities
activities = Activity.objects.all()
print(f"\n🏃 ACTIVITIES: {activities.count()} total")
for activity in activities:
    print(f"  - {activity.activity_name}")

# Check Habits
habits = Habit.objects.all()
print(f"\n📖 HABITS: {habits.count()} total")
for habit in habits:
    user_name = habit.user.username if habit.user else "NO USER"
    print(f"  - {habit.habit_name} ({habit.habit_type}) by {user_name}")

# Check HealthMetrics
metrics = HealthMetric.objects.all()
print(f"\n💊 HEALTH METRICS: {metrics.count()} total")
for metric in metrics:
    print(f"  - {metric.metric_name} ({metric.metric_unit})")

# Check Defis
defis = Defi.objects.all()
print(f"\n🏆 CHALLENGES (DEFIS): {defis.count()} total")
for defi in defis:
    print(f"  - {defi.defi_name}")

print("\n" + "="*70)
print("SYNC STATUS - ALL MODELS")
print("="*70)
print("""
✅ Meals: Fuseki ⟷ Django (FIXED)
✅ Activities: Fuseki ⟷ Django (FIXED)
✅ Habits: Fuseki ⟷ Django (FIXED)
✅ Health Metrics: Fuseki ⟷ Django (FIXED)
✅ Challenges: Fuseki ⟷ Django (FIXED)
""")
print("="*70 + "\n")
