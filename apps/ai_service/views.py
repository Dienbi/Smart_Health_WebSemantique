from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
# Updated regex patterns for meal sync - v2
from django.conf import settings
from apps.sparql_service.client import SparqlClient
from apps.sparql_service.formatter import SparqlResultFormatter
from .gemini_service import GeminiAIService
import logging
import re

logger = logging.getLogger(__name__)


def sync_insert_from_fuseki_to_django(sparql_query, user_id=None):
    """
    Synchronize INSERT operations from Fuseki to Django
    Detects INSERT operations and creates corresponding Django objects
    """
    try:
        from datetime import datetime
        from django.utils import timezone
        from apps.users.models import User
        from apps.meals.models import Meal, FoodItem, Breakfast, Lunch, Dinner, Snack
        from apps.activities.models import Activity, ActivityLog, Cardio, Musculation, Natation
        from apps.habits.models import Habit, HabitLog
        from apps.health_records.models import HealthRecord, HealthMetric
        
        if 'INSERT DATA' not in sparql_query.upper():
            return False
        
        # Log the SPARQL query for debugging
        print("=" * 80)
        print("🔥 SYNC INSERT v4.0 - CALLED!")
        print("=" * 80)
        logger.info(f"=== SYNC INSERT FROM FUSEKI v3.0 - ALL ENTITY TYPES ===")
        logger.info(f"SPARQL Query:\n{sparql_query}")
        logger.info(f"User ID: {user_id}")
        logger.info(f"[SYNC START] Function called successfully")
        
        # Get default user
        try:
            if user_id:
                user = User.objects.get(user_id=user_id)
            else:
                user = User.objects.first()
                if not user:
                    logger.warning("No users found in Django database")
                    return False
        except User.DoesNotExist:
            logger.warning(f"User {user_id} not found in Django")
            return False
        
        logger.info(f"Using user: {user.username} (ID: {user.user_id})")
        
        # Parse Meal INSERT operations - Try multiple patterns
        # Pattern 1: Standard format with meal_name and total_calories
        # Matches: sh:Meal_xxx or sh:Breakfast_xxx or sh:Lunch_xxx or sh:Dinner_xxx or sh:Snack_xxx
        meal_pattern1 = r'sh:(?:Meal|Breakfast|Lunch|Dinner|Snack)_\w+\s+a\s+sh:(Breakfast|Lunch|Dinner|Snack)[^}]*sh:meal_name\s+"([^"]+)"[^}]*sh:total_calories\s+(\d+)'
        # Pattern 2: Alternative naming with name_meal and calories_total
        meal_pattern2 = r'sh:(?:Meal|Breakfast|Lunch|Dinner|Snack)_\w+\s+a\s+sh:(Breakfast|Lunch|Dinner|Snack)[^}]*sh:name_meal\s+"([^"]+)"[^}]*sh:calories_total\s+(\d+)'
        # Pattern 3: AI short form - exactly calories then name (fixed order)
        meal_pattern3 = r'sh:(?:Meal|Breakfast|Lunch|Dinner|Snack)_\w+\s+a\s+sh:(Breakfast|Lunch|Dinner|Snack)\s*;\s*sh:calories\s+(\d+)\s*;\s*sh:name\s+"([^"]+)"'
        # Pattern 4: Flexible order - calories then name
        meal_pattern4 = r'sh:(?:Meal|Breakfast|Lunch|Dinner|Snack)_\w+\s+a\s+sh:(Breakfast|Lunch|Dinner|Snack)[^}]*sh:calories\s+(\d+)[^}]*sh:name\s+"([^"]+)"'
        # Pattern 5: Flexible order - name then calories
        meal_pattern5 = r'sh:(?:Meal|Breakfast|Lunch|Dinner|Snack)_\w+\s+a\s+sh:(Breakfast|Lunch|Dinner|Snack)[^}]*sh:name\s+"([^"]+)"[^}]*sh:calories\s+(\d+)'
        
        meal_type = None
        meal_name = None
        calories = None
        
        match = re.search(meal_pattern1, sparql_query, re.IGNORECASE | re.DOTALL)
        if match:
            meal_type = match.group(2).upper()
            meal_name = match.group(3)
            calories = int(match.group(4))
            logger.info(f"Detected INSERT for Meal (pattern 1 - meal_name): {meal_name} ({meal_type})")
        
        if not match:
            match = re.search(meal_pattern2, sparql_query, re.IGNORECASE | re.DOTALL)
            if match:
                meal_type = match.group(2).upper()
                meal_name = match.group(3)
                calories = int(match.group(4))
                logger.info(f"Detected INSERT for Meal (pattern 2 - name_meal): {meal_name} ({meal_type})")
        
        if not match:
            match = re.search(meal_pattern3, sparql_query, re.IGNORECASE | re.DOTALL)
            if match:
                meal_type = match.group(1).upper()
                calories = int(match.group(2))
                meal_name = match.group(3)
                logger.info(f"Detected INSERT for Meal (pattern 3 - AI short): {meal_name} ({meal_type})")
        
        if not match:
            match = re.search(meal_pattern4, sparql_query, re.IGNORECASE | re.DOTALL)
            if match:
                meal_type = match.group(1).upper()
                calories = int(match.group(2))
                meal_name = match.group(3)
                logger.info(f"Detected INSERT for Meal (pattern 4 - calories first): {meal_name} ({meal_type})")
        
        if not match:
            match = re.search(meal_pattern5, sparql_query, re.IGNORECASE | re.DOTALL)
            if match:
                meal_type = match.group(1).upper()
                meal_name = match.group(2)
                calories = int(match.group(3))
                logger.info(f"Detected INSERT for Meal (pattern 5 - name first): {meal_name} ({meal_type})")
        
        if not match and not meal_name:
            logger.warning(f"No meal pattern matched in SPARQL query")
            logger.warning(f"Query was: {sparql_query}")
        
        # Check if we successfully extracted meal data
        print(f"🔍 MEAL CHECK - meal_type: {meal_type}, meal_name: {meal_name}, calories: {calories}")
        if meal_type and meal_name and calories:
            print(f"🍽️ CREATING MEAL: {meal_name} ({meal_type}) - {calories} cal for user {user.username}")
            logger.info(f"Creating Meal in Django: {meal_name} ({meal_type}) - {calories} cal")
            
            try:
                # Create Meal in Django
                meal = Meal.objects.create(
                    user=user,
                    meal_name=meal_name,
                    meal_type=meal_type,
                    total_calories=calories,
                    meal_date=timezone.now()
                )
                print(f"✅ MEAL CREATED in Django: ID={meal.meal_id}, Name={meal.meal_name}, User={meal.user.username}")
                
                # Create meal type details
                if meal_type == 'BREAKFAST':
                    Breakfast.objects.create(meal=meal, breakfast_score=70)
                elif meal_type == 'LUNCH':
                    Lunch.objects.create(meal=meal, lunch_score=70)
                elif meal_type == 'DINNER':
                    Dinner.objects.create(meal=meal, dinner_score=70)
                elif meal_type == 'SNACK':
                    Snack.objects.create(meal=meal, snack_score=70)
                
                print(f"✅ MEAL SUBTYPE CREATED: {meal_type}")
                logger.info(f"✅ SUCCESS: Meal '{meal_name}' created in Django with ID: {meal.meal_id}")
                # Don't return here - continue checking other entity types
            except Exception as e:
                import traceback
                logger.error(f"❌ ERROR creating meal in Django: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
        
        print("🔍 CHECKPOINT 1: After meal section")
        logger.info(f"[SYNC DEBUG] ✅ Reached after meal section - checking other entity types...")
        
        # Parse Activity INSERT operations
        # Match both old format (sh:Activity_xxx) and new format (sh:Cardio_xxx, sh:Musculation_xxx, sh:Natation_xxx)
        print("🔍 CHECKPOINT 2: About to check activity pattern")
        logger.info(f"[ACTIVITY DEBUG] Checking SPARQL for Activity pattern...")
        logger.info(f"[ACTIVITY DEBUG] SPARQL Query: {sparql_query[:500]}")  # Log first 500 chars
        activity_pattern = r'sh:(?:Activity|Cardio|Musculation|Natation)_\w+\s+a\s+sh:(Cardio|Musculation|Natation)[^}]*sh:activity_name\s+"([^"]+)"'
        match = re.search(activity_pattern, sparql_query, re.IGNORECASE | re.DOTALL)
        print(f"🔍 CHECKPOINT 3: Pattern match result: {match}")
        logger.info(f"[ACTIVITY DEBUG] Pattern match result: {match}")
        
        if match:
            print("🔍 CHECKPOINT 4: Inside activity match block!")
            activity_type = match.group(1)
            activity_name = match.group(2)
            
            print(f"🔍 CHECKPOINT 5: Extracted - Type: {activity_type}, Name: {activity_name}")
            logger.info(f"[ACTIVITY SYNC] ✅ Pattern matched!")
            logger.info(f"[ACTIVITY SYNC] Type: {activity_type}, Name: {activity_name}")
            logger.info(f"[ACTIVITY SYNC] User: {user.username} (ID: {user.user_id})")
            logger.info(f"[ACTIVITY SYNC] Creating Activity in Django...")
            
            try:
                print("🔍 CHECKPOINT 6: About to create Activity object")
                # Create Activity in Django (Activity model doesn't have user field, activities are global)
                activity = Activity.objects.create(
                    activity_name=activity_name,
                    activity_description=f"AI-created {activity_type} activity"
                )
                print(f"🔍 CHECKPOINT 7: Activity created with ID: {activity.activity_id}")
                
                # Create activity type details
                print(f"🔍 Creating subtype for: {activity_type}")
                if activity_type.lower() == 'cardio':
                    print("🔍 Creating Cardio...")
                    cardio = Cardio.objects.create(
                        activity=activity,
                        calories_burned=200,
                        heart_rate=120
                    )
                    print(f"🔍 Cardio created: {cardio}")
                elif activity_type.lower() == 'musculation':
                    print("🔍 Creating Musculation...")
                    musc = Musculation.objects.create(
                        activity=activity,
                        sets=3,
                        repetitions=10,
                        weight=20
                    )
                    print(f"🔍 Musculation created: {musc}")
                elif activity_type.lower() == 'natation':
                    print("🔍 Creating Natation...")
                    nat = Natation.objects.create(
                        activity=activity,
                        distance=500,
                        style='FREESTYLE'
                    )
                    print(f"🔍 Natation created: {nat}")
                
                # Also create an ActivityLog so it appears in the front office
                print("🔍 CHECKPOINT 8a: Creating ActivityLog for front office display")
                from django.utils import timezone
                activity_log = ActivityLog.objects.create(
                    activity=activity,
                    user=user,
                    date=timezone.now(),
                    duration=30,  # Default 30 minutes
                    intensity='MEDIUM'  # Default medium intensity
                )
                print(f"🔍 ActivityLog created with ID: {activity_log.activity_log_id}")
                
                print(f"🔍 CHECKPOINT 8: ✅ SUCCESS! Activity created and type details added")
                logger.info(f"[ACTIVITY SYNC] ✅ SUCCESS! Activity '{activity_name}' created in Django with ID: {activity.activity_id}")
                logger.info(f"[ACTIVITY SYNC] Activity type details and ActivityLog created for: {activity_type}")
            except Exception as activity_error:
                import traceback
                print(f"🔍 CHECKPOINT 9: ❌ ERROR: {str(activity_error)}")
                logger.error(f"[ACTIVITY SYNC] ❌ ERROR creating activity in Django: {str(activity_error)}")
                logger.error(f"[ACTIVITY SYNC] Traceback: {traceback.format_exc()}")
            # Don't return here - continue checking other entity types
        
        # Parse Habit INSERT operations
        # Match both old format (sh:Habit_xxx) and new format (sh:Reading_xxx, sh:Cooking_xxx, sh:Other_xxx, etc.)
        habit_pattern = r'sh:(?:Habit|Reading|Cooking|Drawing|Journaling|Other)_\w+\s+a\s+sh:(Reading|Cooking|Drawing|Journaling|Other)[^}]*sh:habit_name\s+"([^"]+)"'
        match = re.search(habit_pattern, sparql_query, re.IGNORECASE | re.DOTALL)
        
        if match:
            habit_type = match.group(1).upper()
            habit_name = match.group(2)
            
            logger.info(f"Detected INSERT for Habit: {habit_name} ({habit_type}) - User: {user.username}")
            
            # Create Habit in Django
            habit = Habit.objects.create(
                user=user,
                habit_name=habit_name,
                habit_type=habit_type
            )
            
            logger.info(f"✅ SUCCESS: Habit '{habit_name}' created in Django with ID: {habit.habit_id}")
            # Don't return here - continue checking other entity types
        
        # Parse HealthMetric INSERT operations
        # Match various HealthMetric subclasses: HeartRate, Cholesterol, SugarLevel, Oxygen, Weight, Height
        metric_pattern = r'sh:(?:\w+)\s+a\s+sh:(?:HealthMetric|HeartRate|Cholesterol|SugarLevel|Oxygen|Weight|Height)[^}]*sh:healthMetricName\s+"([^"]+)"[^}]*sh:healthMetricUnit\s+"([^"]*)"'
        match = re.search(metric_pattern, sparql_query, re.IGNORECASE | re.DOTALL)
        
        print(f"🔍 HEALTH METRIC CHECK - Pattern matched: {match is not None}")
        if match:
            metric_name = match.group(1)
            metric_unit = match.group(2)
            
            # Try to extract metric value if present
            value_match = re.search(r'sh:healthMetricValue\s+(\d+\.?\d*)', sparql_query, re.IGNORECASE)
            metric_value = float(value_match.group(1)) if value_match else 0.0
            
            print(f"🏥 CREATING HEALTH METRIC: {metric_name} ({metric_unit}) = {metric_value} for user {user.username}")
            logger.info(f"Detected INSERT for HealthMetric: {metric_name} - User: {user.username}")
            
            try:
                # Create HealthMetric
                metric = HealthMetric.objects.create(
                    metric_name=metric_name,
                    metric_description=f"AI-created metric for {user.username}",
                    metric_unit=metric_unit
                )
                print(f"✅ HEALTH METRIC CREATED: ID={metric.health_metric_id}, Name={metric.metric_name}")
                
                # Create HealthRecord to link metric to user
                health_record = HealthRecord.objects.create(
                    user=user,
                    health_metric=metric,
                    value=metric_value,
                    description=f"AI-created health record for {metric_name}",
                    start_date=timezone.now()
                )
                print(f"✅ HEALTH RECORD CREATED: ID={health_record.health_record_id}, User={user.username}, Metric={metric.metric_name}")
                
                logger.info(f"✅ SUCCESS: HealthMetric '{metric_name}' and HealthRecord created in Django")
                logger.info(f"   Metric ID: {metric.health_metric_id}, Record ID: {health_record.health_record_id}")
            except Exception as health_error:
                import traceback
                print(f"❌ ERROR creating health metric/record: {str(health_error)}")
                logger.error(f"Error creating health metric/record: {str(health_error)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
            # Don't return here - continue checking other entity types
        
        # Parse Defi (Challenge) INSERT operations
        defi_pattern = r'sh:(?:Defi|Challenge)_\w+\s+a\s+sh:Defi[^}]*sh:defi_name\s+"([^"]+)"'
        match = re.search(defi_pattern, sparql_query, re.IGNORECASE | re.DOTALL)
        
        if match:
            defi_name = match.group(1)
            
            # Try to extract description if present
            desc_match = re.search(r'sh:defi_description\s+"([^"]+)"', sparql_query, re.IGNORECASE)
            defi_description = desc_match.group(1) if desc_match else f"AI-created challenge: {defi_name}"
            
            logger.info(f"Detected INSERT for Defi: {defi_name}")
            
            # Import here to avoid circular imports
            from apps.defis.models import Defi
            
            # Create Defi in Django
            defi = Defi.objects.create(
                defi_name=defi_name,
                defi_description=defi_description
            )
            
            logger.info(f"✅ SUCCESS: Defi '{defi_name}' created in Django with ID: {defi.defi_id}")
            # Don't return here - continue checking other entity types
        
        # Return True if any entity was created, False otherwise
        # We can check if any pattern matched by seeing if we got past the initial checks
        return True  # If we got here without exceptions, sync succeeded or found nothing to sync
        
    except Exception as e:
        import traceback
        logger.error(f"Error in sync_insert_from_fuseki_to_django: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


def sync_delete_from_fuseki_to_django(sparql_query):
    """
    Synchronize DELETE operations from Fuseki to Django
    Detects DELETE operations and deletes corresponding Django objects
    """
    try:
        # Check if it's a DELETE operation
        if 'DELETE' not in sparql_query.upper():
            return False
        
        print("=" * 80)
        print("🗑️ SYNC DELETE - Processing DELETE operation")
        print("=" * 80)
        
        # Parse Habit DELETE operations
        # Pattern: DELETE WHERE { ?h sh:habit_name "test" . ?h ?p ?o }
        habit_pattern = r'sh:habit_name\s+"([^"]+)"'
        match = re.search(habit_pattern, sparql_query, re.IGNORECASE)
        
        if match:
            habit_name = match.group(1)
            print(f"🔍 HABIT DELETE detected: {habit_name}")
            logger.info(f"Detected DELETE operation for Habit: {habit_name}")
            
            from apps.habits.models import Habit
            
            try:
                habit = Habit.objects.get(habit_name=habit_name)
                habit_id = habit.habit_id
                habit.delete()
                print(f"✅ HABIT DELETED from Django: {habit_name} (ID: {habit_id})")
                logger.info(f"Habit '{habit_name}' (ID: {habit_id}) deleted from Django")
                return True
            except Habit.DoesNotExist:
                print(f"⚠️ Habit '{habit_name}' not found in Django")
                logger.warning(f"Habit '{habit_name}' not found in Django, skipping sync")
                return False
            except Exception as e:
                print(f"❌ ERROR deleting habit: {str(e)}")
                logger.error(f"Error deleting Habit '{habit_name}' from Django: {str(e)}")
                return False
        
        # Parse Activity DELETE operations
        # Pattern: DELETE WHERE { ?a sh:activity_name "Running" . ?a ?p ?o }
        activity_pattern = r'sh:activity_name\s+"([^"]+)"'
        match = re.search(activity_pattern, sparql_query, re.IGNORECASE)
        
        if match:
            activity_name = match.group(1)
            print(f"🔍 ACTIVITY DELETE detected: {activity_name}")
            logger.info(f"Detected DELETE operation for Activity: {activity_name}")
            
            from apps.activities.models import Activity
            
            try:
                activity = Activity.objects.get(activity_name=activity_name)
                activity_id = activity.activity_id
                activity.delete()
                print(f"✅ ACTIVITY DELETED from Django: {activity_name} (ID: {activity_id})")
                logger.info(f"Activity '{activity_name}' (ID: {activity_id}) deleted from Django")
                return True
            except Activity.DoesNotExist:
                print(f"⚠️ Activity '{activity_name}' not found in Django")
                logger.warning(f"Activity '{activity_name}' not found in Django, skipping sync")
                return False
            except Exception as e:
                print(f"❌ ERROR deleting activity: {str(e)}")
                logger.error(f"Error deleting Activity '{activity_name}' from Django: {str(e)}")
                return False
        
        # Parse Meal DELETE operations
        # Pattern: DELETE WHERE { ?m sh:name "pancakes" . ?m ?p ?o }
        meal_pattern = r'\?m\s+sh:name\s+"([^"]+)"'
        match = re.search(meal_pattern, sparql_query, re.IGNORECASE)
        
        if match:
            meal_name = match.group(1)
            print(f"🔍 MEAL DELETE detected: {meal_name}")
            logger.info(f"Detected DELETE operation for Meal: {meal_name}")
            
            from apps.meals.models import Meal
            
            try:
                meal = Meal.objects.get(meal_name=meal_name)
                meal_id = meal.meal_id
                meal.delete()
                print(f"✅ MEAL DELETED from Django: {meal_name} (ID: {meal_id})")
                logger.info(f"Meal '{meal_name}' (ID: {meal_id}) deleted from Django")
                return True
            except Meal.DoesNotExist:
                print(f"⚠️ Meal '{meal_name}' not found in Django")
                logger.warning(f"Meal '{meal_name}' not found in Django, skipping sync")
                return False
            except Exception as e:
                print(f"❌ ERROR deleting meal: {str(e)}")
                logger.error(f"Error deleting Meal '{meal_name}' from Django: {str(e)}")
                return False
        
        # Parse Defi DELETE operations
        # Pattern: DELETE WHERE { ?d sh:defi_name "challenge" . ?d ?p ?o }
        defi_pattern = r'sh:defi_name\s+"([^"]+)"'
        match = re.search(defi_pattern, sparql_query, re.IGNORECASE)
        
        if match:
            defi_name = match.group(1)
            print(f"🔍 DEFI DELETE detected: {defi_name}")
            logger.info(f"Detected DELETE operation for Defi: {defi_name}")
            
            from apps.defis.models import Defi
            
            try:
                defi = Defi.objects.get(defi_name=defi_name)
                defi_id = defi.defi_id
                defi.delete()
                print(f"✅ DEFI DELETED from Django: {defi_name} (ID: {defi_id})")
                logger.info(f"Defi '{defi_name}' (ID: {defi_id}) deleted from Django")
                return True
            except Defi.DoesNotExist:
                print(f"⚠️ Defi '{defi_name}' not found in Django")
                logger.warning(f"Defi '{defi_name}' not found in Django, skipping sync")
                return False
            except Exception as e:
                print(f"❌ ERROR deleting defi: {str(e)}")
                logger.error(f"Error deleting Defi '{defi_name}' from Django: {str(e)}")
                return False
        
        # Parse HealthMetric DELETE operations
        # Pattern: DELETE WHERE { ?metric sh:healthMetricName "name" . ?metric ?p ?o }
        health_metric_pattern = r'sh:healthMetricName\s+"([^"]+)"'
        match = re.search(health_metric_pattern, sparql_query, re.IGNORECASE)
        # Parse HealthMetric DELETE operations
        # Pattern: DELETE WHERE { ?metric sh:healthMetricName "name" . ?metric ?p ?o }
        health_metric_pattern = r'sh:healthMetricName\s+"([^"]+)"'
        match = re.search(health_metric_pattern, sparql_query, re.IGNORECASE)
        
        if match:
            metric_name = match.group(1)
            print(f"🔍 HEALTH METRIC DELETE detected: {metric_name}")
            logger.info(f"Detected DELETE operation for HealthMetric: {metric_name}")
            
            from apps.health_records.models import HealthMetric
            
            try:
                metric = HealthMetric.objects.get(metric_name=metric_name)
                metric_id = metric.health_metric_id
                metric.delete()
                print(f"✅ HEALTH METRIC DELETED from Django: {metric_name} (ID: {metric_id})")
                logger.info(f"HealthMetric '{metric_name}' (ID: {metric_id}) deleted from Django")
                return True
            except HealthMetric.DoesNotExist:
                print(f"⚠️ HealthMetric '{metric_name}' not found in Django")
                logger.warning(f"HealthMetric '{metric_name}' not found in Django, skipping sync")
                return False
            except Exception as e:
                print(f"❌ ERROR deleting health metric: {str(e)}")
                logger.error(f"Error deleting HealthMetric '{metric_name}' from Django: {str(e)}")
                return False
        
        # Parse HealthRecord DELETE operations
        # Pattern: DELETE WHERE { ?record sh:healthRecordId 123 . ?record ?p ?o }
        health_record_pattern = r'sh:healthRecordId\s+(\d+)'
        match = re.search(health_record_pattern, sparql_query, re.IGNORECASE)
        
        if match:
            record_id = int(match.group(1))
            print(f"🔍 HEALTH RECORD DELETE detected: ID={record_id}")
            logger.info(f"Detected DELETE operation for HealthRecord: {record_id}")
            
            from apps.health_records.models import HealthRecord
            
            try:
                record = HealthRecord.objects.get(health_record_id=record_id)
                record.delete()
                print(f"✅ HEALTH RECORD DELETED from Django: ID={record_id}")
                logger.info(f"HealthRecord (ID: {record_id}) deleted from Django")
                return True
            except HealthRecord.DoesNotExist:
                print(f"⚠️ HealthRecord ID={record_id} not found in Django")
                logger.warning(f"HealthRecord (ID: {record_id}) not found in Django, skipping sync")
                return False
            except Exception as e:
                print(f"❌ ERROR deleting health record: {str(e)}")
                logger.error(f"Error deleting HealthRecord (ID: {record_id}) from Django: {str(e)}")
                return False
        
        print("⚠️ No matching DELETE pattern found")
        return False
        
    except Exception as e:
        import traceback
        print(f"❌ ERROR in sync_delete: {str(e)}")
        logger.error(f"Error in sync_delete_from_fuseki_to_django: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


# ============================================================================
# API VIEWS
# ============================================================================


@method_decorator(csrf_exempt, name='dispatch')
class AIQueryView(APIView):
    """API endpoint for AI-powered queries"""
    permission_classes = [AllowAny]  # Allow unauthenticated access for testing
    authentication_classes = []  # Disable authentication for testing
    
    def post(self, request):
        """Process natural language prompt using real AI"""
        prompt = request.data.get('prompt', '')
        user_id = request.data.get('user_id', None)
        
        if not prompt:
            return Response(
                {'error': 'Prompt is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Initialize AI service
            ai_service = GeminiAIService()
            
            # Check if AI is configured
            if not ai_service.enabled:
                return Response({
                    'success': False,
                    'error': 'AI service not configured',
                    'setup_instructions': [
                        '1. Get free API key: https://makersuite.google.com/app/apikey',
                        '2. Add to .env file: GEMINI_API_KEY=your_key_here',
                        '3. Restart Django server'
                    ]
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            # Extract user ID if not provided
            if not user_id:
                entities = ai_service.extract_entities(prompt)
                user_id = entities.get('user_id')
            
            # Analyze intent using AI
            intent = ai_service.analyze_intent(prompt)
            
            # Generate SPARQL query using AI
            try:
                sparql_query, error = ai_service.generate_sparql(prompt, user_id)
                
                if error:
                    return Response({
                        'success': False,
                        'error': error,
                        'prompt': prompt
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as ai_error:
                import traceback
                logger.error(f"Error generating SPARQL query: {str(ai_error)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                return Response({
                    'success': False,
                    'error': f'Error generating SPARQL query: {str(ai_error)}',
                    'prompt': prompt,
                    'traceback': traceback.format_exc() if settings.DEBUG else None
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Execute query based on intent
            client = SparqlClient()
            
            # Log the generated SPARQL for debugging
            logger.info(f"📝 Generated SPARQL Query:")
            logger.info(f"{sparql_query}")
            
            # Determine if it's a modification query
            is_modification = any(keyword in sparql_query.upper() for keyword in ['INSERT', 'DELETE', 'UPDATE'])
            logger.info(f"🔍 Is modification query: {is_modification}")
            
            if is_modification:
                # Execute update query
                try:
                    # Log the SPARQL query before execution
                    print("=" * 80)
                    print("🔍 EXECUTING SPARQL UPDATE:")
                    print(sparql_query)
                    print("=" * 80)
                    
                    # Execute the SPARQL update in Fuseki
                    success = client.execute_update(sparql_query)
                    
                    if success:
                        # Get operation type
                        operation = 'unknown'
                        if 'INSERT DATA' in sparql_query.upper():
                            operation = 'insert'
                            logger.info(f"🔄 SPARQL INSERT detected - attempting sync...")
                            logger.info(f"   User ID: {user_id}")
                            logger.info(f"   SPARQL Query:\n{sparql_query}")
                            
                            # Synchronize INSERT operations from Fuseki to Django AFTER executing
                            sync_result = sync_insert_from_fuseki_to_django(sparql_query, user_id)
                            if not sync_result:
                                logger.warning("⚠️ Sync to Django failed or no entities recognized")
                                logger.warning(f"   Check if SPARQL matches expected patterns")
                            else:
                                logger.info("✅ Successfully synced INSERT to Django")
                                logger.info(f"   Created: {sync_result}")
                        elif 'DELETE' in sparql_query.upper() and 'INSERT' in sparql_query.upper():
                            operation = 'update'
                        elif 'DELETE' in sparql_query.upper():
                            operation = 'delete'
                            # Synchronize DELETE operations from Fuseki to Django AFTER executing
                            sync_delete_from_fuseki_to_django(sparql_query)
                        
                        return Response({
                            'success': True,
                            'prompt': prompt,
                            'intent': intent,
                            'action': operation,
                            'user_id': user_id,
                            'sparql_query': sparql_query,
                            'message': f'Data {operation}ed successfully and synced to database',
                            'ai_powered': True,
                            'ai_model': 'Google Gemini Pro'
                        })
                    else:
                        return Response({
                            'success': False,
                            'error': 'Failed to execute modification query',
                            'sparql_query': sparql_query
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                except Exception as e:
                    import urllib.error
                    import traceback
                    error_msg = str(e)
                    error_type = type(e).__name__
                    
                    # Log the malformed SPARQL for debugging
                    if 'Parse error' in error_msg or 'badly formed' in error_msg or 'QueryBadFormed' in error_msg:
                        logger.error(f"❌ MALFORMED SPARQL QUERY:")
                        logger.error(f"Error: {error_msg}")
                        logger.error(f"SPARQL:\n{sparql_query}")
                        return Response({
                            'success': False,
                            'error': f'Malformed SPARQL query: {error_msg}',
                            'sparql_query': sparql_query,
                            'hint': 'The AI generated invalid SPARQL syntax. Please try rephrasing your request.'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Check for connection errors (more comprehensive)
                    is_connection_error = (
                        isinstance(e, urllib.error.URLError) or
                        isinstance(e, ConnectionError) or
                        'ConnectionRefusedError' in error_msg or
                        'WinError 10061' in error_msg or
                        'Connection refused' in error_msg.lower() or
                        'cannot connect' in error_msg.lower() or
                        'target machine actively refused' in error_msg.lower() or
                        error_type == 'ConnectionRefusedError'
                    )
                    
                    if is_connection_error:
                        return Response({
                            'success': False,
                            'error': 'Fuseki server is not running',
                            'message': 'Cannot connect to Fuseki server. Please start Fuseki server first.',
                            'setup_instructions': [
                                '1. Start Fuseki server:',
                                '   Option A - Using Docker:',
                                '   docker-compose up -d fuseki',
                                '   ',
                                '   Option B - Manual (if installed):',
                                '   cd C:\\apache-jena-fuseki-5.2.0',
                                '   .\\fuseki-server.bat --update --mem /smarthealth',
                                '2. Verify Fuseki is running at: http://localhost:3030',
                                '3. Retry your operation after starting Fuseki'
                            ],
                            'sparql_query': sparql_query,
                            'error_details': error_msg if settings.DEBUG else None
                        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                    else:
                        # Log the error for debugging
                        logger.error(f"SPARQL update error: {error_msg}")
                        logger.error(f"SPARQL query: {sparql_query}")
                        logger.error(f"Error type: {error_type}")
                        if settings.DEBUG:
                            logger.error(f"Traceback: {traceback.format_exc()}")
                        
                        return Response({
                            'success': False,
                            'error': f'Error executing SPARQL update: {error_msg}',
                            'message': 'The SPARQL query failed. Please check the query syntax and try again.',
                            'sparql_query': sparql_query,
                            'error_type': error_type,
                            'traceback': traceback.format_exc() if settings.DEBUG else None
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                # Execute select query
                try:
                    results = client.execute_query(sparql_query)
                    
                    # Format results
                    try:
                        formatted_results = SparqlResultFormatter.format_results(results)
                        results_count = len(formatted_results) if formatted_results else 0
                    except Exception as format_error:
                        import traceback
                        logger.error(f"Error formatting SPARQL results: {str(format_error)}")
                        logger.error(f"Raw results: {results}")
                        logger.error(f"Traceback: {traceback.format_exc()}")
                        return Response({
                            'success': False,
                            'error': f'Error formatting SPARQL results: {str(format_error)}',
                            'sparql_query': sparql_query,
                            'raw_results': results if settings.DEBUG else None,
                            'traceback': traceback.format_exc() if settings.DEBUG else None
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
                    # Return successful response
                    try:
                        return Response({
                            'success': True,
                            'prompt': prompt,
                            'intent': intent,
                            'action': 'query',
                            'user_id': user_id,
                            'sparql_query': sparql_query,
                            'results_count': results_count,
                            'results': formatted_results,
                            'ai_powered': True,
                            'ai_model': 'Google Gemini Pro'
                        })
                    except Exception as response_error:
                        import traceback
                        logger.error(f"Error creating response: {str(response_error)}")
                        logger.error(f"Traceback: {traceback.format_exc()}")
                        return Response({
                            'success': False,
                            'error': f'Error creating response: {str(response_error)}',
                            'sparql_query': sparql_query,
                            'traceback': traceback.format_exc() if settings.DEBUG else None
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                except Exception as e:
                    import urllib.error
                    import traceback
                    error_msg = str(e)
                    error_type = type(e).__name__
                    
                    # Check for connection errors (more comprehensive)
                    is_connection_error = (
                        isinstance(e, urllib.error.URLError) or
                        isinstance(e, ConnectionError) or
                        'ConnectionRefusedError' in error_msg or
                        'WinError 10061' in error_msg or
                        'Connection refused' in error_msg.lower() or
                        'cannot connect' in error_msg.lower() or
                        'target machine actively refused' in error_msg.lower() or
                        error_type == 'ConnectionRefusedError'
                    )
                    
                    if is_connection_error:
                        return Response({
                            'success': False,
                            'error': 'Fuseki server is not running',
                            'message': 'Cannot connect to Fuseki server. Please start Fuseki server first.',
                            'setup_instructions': [
                                '1. Start Fuseki server:',
                                '   Option A - Using Docker:',
                                '   docker-compose up -d fuseki',
                                '   ',
                                '   Option B - Manual (if installed):',
                                '   cd C:\\apache-jena-fuseki-5.2.0',
                                '   .\\fuseki-server.bat --update --mem /smarthealth',
                                '2. Verify Fuseki is running at: http://localhost:3030',
                                '3. Refresh this page after starting Fuseki'
                            ],
                            'sparql_query': sparql_query,
                            'error_details': error_msg if settings.DEBUG else None
                        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                    else:
                        return Response({
                            'success': False,
                            'error': f'Error executing SPARQL query: {error_msg}',
                            'sparql_query': sparql_query,
                            'error_type': error_type,
                            'traceback': traceback.format_exc() if settings.DEBUG else None
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            error_type = type(e).__name__
            error_msg = str(e)
            
            # Log to console and logger
            logger.error(f"Error in AIQueryView: {error_type}: {error_msg}")
            logger.error(f"Traceback: {error_details}")
            print(f"Error in AIQueryView: {error_type}: {error_msg}")
            print(f"Traceback: {error_details}")
            
            # Return error response
            try:
                return Response(
                    {
                        'success': False,
                        'error': error_msg,
                        'error_type': error_type,
                        'message': 'An error occurred while processing your query',
                        'traceback': error_details if settings.DEBUG else None
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            except Exception as response_error:
                # If even error response fails, return minimal response
                logger.error(f"Failed to create error response: {str(response_error)}")
                return Response(
                    {
                        'success': False,
                        'error': 'Internal server error',
                        'error_type': error_type
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
    
    def get(self, request):
        """Get example prompts and usage information"""
        examples = {
            'query_examples': [
                {
                    'prompt': 'Show me all users',
                    'description': 'Retrieves all users from the system',
                    'type': 'SELECT'
                },
                {
                    'prompt': 'What are the activities for user 1?',
                    'description': 'Gets activity logs for a specific user',
                    'type': 'SELECT'
                },
                {
                    'prompt': 'Show me health metrics for user 1',
                    'description': 'Retrieves health metrics for a specific user',
                    'type': 'SELECT'
                },
                {
                    'prompt': 'What meals does user 1 have?',
                    'description': 'Gets meal information for a specific user',
                    'type': 'SELECT'
                },
                {
                    'prompt': 'Show me all challenges',
                    'description': 'Lists all available challenges',
                    'type': 'SELECT'
                }
            ],
            'insert_examples': [
                {
                    'prompt': 'Add a new user named Alice with email alice@example.com',
                    'description': 'Creates a new user in the system',
                    'type': 'INSERT'
                },
                {
                    'prompt': 'Create a cardio activity called Running',
                    'description': 'Adds a new cardio activity',
                    'type': 'INSERT'
                },
                {
                    'prompt': 'Add a breakfast meal with 500 calories',
                    'description': 'Creates a new breakfast meal entry',
                    'type': 'INSERT'
                },
                {
                    'prompt': 'Create a new challenge called 30-Day Fitness',
                    'description': 'Adds a new challenge/defi',
                    'type': 'INSERT'
                }
            ],
            'update_examples': [
                {
                    'prompt': 'Update user Alice email to newalice@example.com',
                    'description': 'Changes the email of an existing user',
                    'type': 'UPDATE'
                },
                {
                    'prompt': 'Change the duration of Running activity to 45 minutes',
                    'description': 'Modifies an activity\'s duration',
                    'type': 'UPDATE'
                },
                {
                    'prompt': 'Set meal calories to 600 for breakfast',
                    'description': 'Updates the calorie count of a meal',
                    'type': 'UPDATE'
                }
            ],
            'delete_examples': [
                {
                    'prompt': 'Delete user Alice',
                    'description': 'Removes a user from the system',
                    'type': 'DELETE'
                },
                {
                    'prompt': 'Remove activity Running',
                    'description': 'Deletes an activity',
                    'type': 'DELETE'
                },
                {
                    'prompt': 'Delete the breakfast meal',
                    'description': 'Removes a meal entry',
                    'type': 'DELETE'
                }
            ],
            'usage': {
                'endpoint': '/api/ai/query/',
                'method': 'POST',
                'body': {
                    'prompt': 'Your natural language query/command',
                    'user_id': 'Optional: specific user ID (can be extracted from prompt)'
                }
            },
            'capabilities': [
                'Query data with natural language (SELECT)',
                'Insert new data (INSERT)',
                'Update existing data (UPDATE)',
                'Delete data (DELETE)',
                'AI-powered intent detection',
                'Automatic entity extraction'
            ]
        }
        
        return Response(examples)
