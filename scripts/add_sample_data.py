"""
Add sample data to Fuseki for testing
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from apps.sparql_service.client import SparqlClient


def add_sample_data():
    """Add sample users, meals, activities, etc. to Fuseki"""
    
    print("\n" + "="*60)
    print("🌱 Adding Sample Data to Fuseki")
    print("="*60 + "\n")
    
    client = SparqlClient()
    
    # Sample data INSERT query
    insert_query = """
PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

INSERT DATA {
    # Users
    sh:User1 rdf:type sh:User ;
        sh:username "alice" ;
        sh:email "alice@example.com" .
    
    sh:User2 rdf:type sh:User ;
        sh:username "bob" ;
        sh:email "bob@example.com" .
    
    sh:Student1 rdf:type sh:Student ;
        sh:username "charlie" ;
        sh:email "charlie@example.com" ;
        sh:classe "10A" .
    
    sh:Teacher1 rdf:type sh:Teacher ;
        sh:username "diana" ;
        sh:email "diana@example.com" ;
        sh:matier "Physical Education" .
    
    # Meals
    sh:Meal1 rdf:type sh:Breakfast ;
        sh:mealDate "2025-10-30"^^xsd:date ;
        sh:totalCalories 450 .
    
    sh:Meal2 rdf:type sh:Lunch ;
        sh:mealDate "2025-10-30"^^xsd:date ;
        sh:totalCalories 650 .
    
    sh:Meal3 rdf:type sh:Dinner ;
        sh:mealDate "2025-10-29"^^xsd:date ;
        sh:totalCalories 500 .
    
    # Food Items
    sh:Food1 rdf:type sh:FoodItem ;
        sh:foodName "Oatmeal" ;
        sh:calories 300 ;
        sh:protein 10 ;
        sh:carbs 50 .
    
    sh:Food2 rdf:type sh:FoodItem ;
        sh:foodName "Chicken Salad" ;
        sh:calories 400 ;
        sh:protein 35 ;
        sh:carbs 20 .
    
    # Activities
    sh:Activity1 rdf:type sh:Cardio ;
        sh:activityName "Running" ;
        sh:duration 30 ;
        sh:caloriesBurned 300 .
    
    sh:Activity2 rdf:type sh:Musculation ;
        sh:activityName "Weight Training" ;
        sh:duration 45 ;
        sh:sets 3 ;
        sh:reps 12 .
    
    # Health Records
    sh:HealthRecord1 rdf:type sh:HealthRecord ;
        sh:recordDate "2025-10-30"^^xsd:date .
    
    # Health Metrics
    sh:Metric1 rdf:type sh:HeartRate ;
        sh:value 75 ;
        sh:unit "bpm" .
    
    sh:Metric2 rdf:type sh:Weight ;
        sh:value 70 ;
        sh:unit "kg" .
    
    # Habits
    sh:Habit1 rdf:type sh:Reading ;
        sh:habitName "Daily Reading" ;
        sh:frequency "daily" .
    
    sh:Habit2 rdf:type sh:Cooking ;
        sh:habitName "Meal Prep" ;
        sh:frequency "weekly" .
    
    # Challenges
    sh:Defi1 rdf:type sh:Defi ;
        sh:defiName "30-Day Fitness Challenge" ;
        sh:startDate "2025-10-01"^^xsd:date ;
        sh:endDate "2025-10-31"^^xsd:date .
    
    # Relationships
    sh:User1 sh:hasMeal sh:Meal1 .
    sh:User1 sh:hasMeal sh:Meal2 .
    sh:User2 sh:hasMeal sh:Meal3 .
    
    sh:Meal1 sh:hasFoodItem sh:Food1 .
    sh:Meal2 sh:hasFoodItem sh:Food2 .
    
    sh:User1 sh:PerformsActivity sh:Activity1 .
    sh:User2 sh:PerformsActivity sh:Activity2 .
    
    sh:User1 sh:hasHealthRecord sh:HealthRecord1 .
    sh:HealthRecord1 sh:containsMetric sh:Metric1 .
    sh:HealthRecord1 sh:containsMetric sh:Metric2 .
    
    sh:User1 sh:hasHabit sh:Habit1 .
    sh:User2 sh:hasHabit sh:Habit2 .
    
    sh:User1 sh:hasParticipation sh:Participation1 .
    sh:Participation1 rdf:type sh:Participation ;
        sh:progress 50 ;
        sh:status "active" .
}
"""
    
    print("📤 Inserting sample data...")
    print(f"Query length: {len(insert_query)} characters\n")
    
    try:
        # Execute the INSERT query
        result = client.execute_update(insert_query)
        
        print("✅ Sample data added successfully!\n")
        print("Added:")
        print("  - 4 Users (2 regular, 1 student, 1 teacher)")
        print("  - 3 Meals (breakfast, lunch, dinner)")
        print("  - 2 Food Items")
        print("  - 2 Activities (cardio, strength)")
        print("  - 1 Health Record with 2 metrics")
        print("  - 2 Habits")
        print("  - 1 Challenge")
        print("  - Multiple relationships")
        
        print("\n🎉 You can now query for real data!")
        print("\nTry these queries:")
        print('  - "Show me all meals"')
        print('  - "List all users"')
        print('  - "What activities are there?"')
        print('  - "Show meals for user alice"')
        
    except Exception as e:
        print(f"❌ Error inserting data: {str(e)}")
        print("\nMake sure:")
        print("1. Fuseki server is running")
        print("2. Dataset 'smarthealth' exists")
        print("3. Update permissions are enabled")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    add_sample_data()
