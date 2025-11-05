"""
Script de test pour le CRUD FoodItem
Ce script crée des données de test pour tester l'interface admin des FoodItems
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smart_Health.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.meals.models import Meal, FoodItem, Calories, Protein, Carbs, Fiber, Sugar
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


def create_test_data():
    """Create test data for FoodItem CRUD"""
    
    print("🚀 Création des données de test pour FoodItem...")
    
    # 1. Create or get admin user
    print("\n1️⃣ Création de l'utilisateur admin...")
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@smarthealth.com',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"   ✅ Admin créé: {admin_user.username}")
    else:
        print(f"   ℹ️  Admin existe déjà: {admin_user.username}")
    
    # 2. Create or get regular user
    print("\n2️⃣ Création d'un utilisateur régulier...")
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@smarthealth.com',
            'first_name': 'Test',
            'last_name': 'User',
        }
    )
    if created:
        user.set_password('test123')
        user.save()
        print(f"   ✅ Utilisateur créé: {user.username}")
    else:
        print(f"   ℹ️  Utilisateur existe déjà: {user.username}")
    
    # 3. Create test meals
    print("\n3️⃣ Création des repas de test...")
    meals_data = [
        {
            'meal_name': 'Petit-déjeuner complet',
            'meal_type': 'BREAKFAST',
            'total_calories': 450,
            'meal_date': timezone.now(),
        },
        {
            'meal_name': 'Déjeuner équilibré',
            'meal_type': 'LUNCH',
            'total_calories': 650,
            'meal_date': timezone.now() + timedelta(hours=4),
        },
        {
            'meal_name': 'Dîner léger',
            'meal_type': 'DINNER',
            'total_calories': 500,
            'meal_date': timezone.now() + timedelta(hours=10),
        },
        {
            'meal_name': 'Snack après-midi',
            'meal_type': 'SNACK',
            'total_calories': 200,
            'meal_date': timezone.now() + timedelta(hours=6),
        },
    ]
    
    meals = []
    for meal_data in meals_data:
        meal, created = Meal.objects.get_or_create(
            user=user,
            meal_name=meal_data['meal_name'],
            defaults=meal_data
        )
        meals.append(meal)
        status = "✅ Créé" if created else "ℹ️  Existe déjà"
        print(f"   {status}: {meal.meal_name}")
    
    # 4. Create test food items with nutrition
    print("\n4️⃣ Création des aliments avec informations nutritionnelles...")
    
    food_items_data = [
        # Breakfast items
        {
            'meal': meals[0],
            'food_item_name': 'Œufs brouillés',
            'food_item_description': 'Deux œufs biologiques brouillés avec du beurre',
            'food_type': 'PROTEIN',
            'nutrition': {
                'calories': 180,
                'protein': 13,
                'carbs': 2,
                'fiber': 0,
                'sugar': 1,
            }
        },
        {
            'meal': meals[0],
            'food_item_name': 'Pain complet',
            'food_item_description': 'Deux tranches de pain complet grillé',
            'food_type': 'CARBS',
            'nutrition': {
                'calories': 160,
                'protein': 6,
                'carbs': 30,
                'fiber': 4,
                'sugar': 3,
            }
        },
        {
            'meal': meals[0],
            'food_item_name': 'Avocat',
            'food_item_description': 'Un demi-avocat frais en tranches',
            'food_type': 'FATS',
            'nutrition': {
                'calories': 120,
                'protein': 2,
                'carbs': 6,
                'fiber': 5,
                'sugar': 0,
            }
        },
        # Lunch items
        {
            'meal': meals[1],
            'food_item_name': 'Poulet grillé',
            'food_item_description': 'Blanc de poulet grillé sans peau (150g)',
            'food_type': 'PROTEIN',
            'nutrition': {
                'calories': 250,
                'protein': 45,
                'carbs': 0,
                'fiber': 0,
                'sugar': 0,
            }
        },
        {
            'meal': meals[1],
            'food_item_name': 'Riz basmati',
            'food_item_description': 'Riz basmati cuit nature (200g)',
            'food_type': 'CARBS',
            'nutrition': {
                'calories': 260,
                'protein': 5,
                'carbs': 56,
                'fiber': 1,
                'sugar': 0,
            }
        },
        {
            'meal': meals[1],
            'food_item_name': 'Brocoli vapeur',
            'food_item_description': 'Brocoli cuit à la vapeur (150g)',
            'food_type': 'VEGETABLES',
            'nutrition': {
                'calories': 50,
                'protein': 4,
                'carbs': 10,
                'fiber': 3,
                'sugar': 2,
            }
        },
        # Dinner items
        {
            'meal': meals[2],
            'food_item_name': 'Saumon grillé',
            'food_item_description': 'Filet de saumon grillé avec citron (120g)',
            'food_type': 'PROTEIN',
            'nutrition': {
                'calories': 220,
                'protein': 25,
                'carbs': 0,
                'fiber': 0,
                'sugar': 0,
            }
        },
        {
            'meal': meals[2],
            'food_item_name': 'Quinoa',
            'food_item_description': 'Quinoa cuit nature (150g)',
            'food_type': 'CARBS',
            'nutrition': {
                'calories': 170,
                'protein': 6,
                'carbs': 30,
                'fiber': 4,
                'sugar': 1,
            }
        },
        {
            'meal': meals[2],
            'food_item_name': 'Salade verte',
            'food_item_description': 'Mélange de laitue, roquette et épinards',
            'food_type': 'VEGETABLES',
            'nutrition': {
                'calories': 25,
                'protein': 2,
                'carbs': 4,
                'fiber': 2,
                'sugar': 1,
            }
        },
        # Snack items
        {
            'meal': meals[3],
            'food_item_name': 'Pomme',
            'food_item_description': 'Pomme rouge moyenne (150g)',
            'food_type': 'FRUITS',
            'nutrition': {
                'calories': 80,
                'protein': 0,
                'carbs': 21,
                'fiber': 4,
                'sugar': 16,
            }
        },
        {
            'meal': meals[3],
            'food_item_name': 'Amandes',
            'food_item_description': 'Amandes non salées (30g)',
            'food_type': 'FATS',
            'nutrition': {
                'calories': 170,
                'protein': 6,
                'carbs': 6,
                'fiber': 4,
                'sugar': 1,
            }
        },
        {
            'meal': meals[3],
            'food_item_name': 'Yaourt grec',
            'food_item_description': 'Yaourt grec nature 0% (150g)',
            'food_type': 'PROTEIN',
            'nutrition': {
                'calories': 90,
                'protein': 15,
                'carbs': 6,
                'fiber': 0,
                'sugar': 5,
            }
        },
    ]
    
    created_count = 0
    for item_data in food_items_data:
        nutrition = item_data.pop('nutrition')
        
        food_item, created = FoodItem.objects.get_or_create(
            meal=item_data['meal'],
            food_item_name=item_data['food_item_name'],
            defaults={
                'food_item_description': item_data['food_item_description'],
                'food_type': item_data['food_type'],
            }
        )
        
        if created:
            created_count += 1
            # Add nutritional information
            Calories.objects.create(food_item=food_item, calories_value=nutrition['calories'])
            Protein.objects.create(food_item=food_item, protein_value=nutrition['protein'])
            Carbs.objects.create(food_item=food_item, carbs_value=nutrition['carbs'])
            Fiber.objects.create(food_item=food_item, fiber_value=nutrition['fiber'])
            Sugar.objects.create(food_item=food_item, sugar_value=nutrition['sugar'])
            
            print(f"   ✅ Créé: {food_item.food_item_name} ({food_item.get_food_type_display()})")
        else:
            print(f"   ℹ️  Existe déjà: {food_item.food_item_name}")
    
    print(f"\n✨ {created_count} nouveaux aliments créés avec succès!")
    
    # 5. Display summary
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DES DONNÉES DE TEST")
    print("="*60)
    print(f"👤 Utilisateurs:")
    print(f"   - Admin: username='admin', password='admin123'")
    print(f"   - User: username='testuser', password='test123'")
    print(f"\n🍽️ Repas créés: {Meal.objects.count()}")
    print(f"🍳 Aliments créés: {FoodItem.objects.count()}")
    print(f"🔥 Entrées nutritionnelles:")
    print(f"   - Calories: {Calories.objects.count()}")
    print(f"   - Protéines: {Protein.objects.count()}")
    print(f"   - Glucides: {Carbs.objects.count()}")
    print(f"   - Fibres: {Fiber.objects.count()}")
    print(f"   - Sucres: {Sugar.objects.count()}")
    
    print("\n" + "="*60)
    print("🎉 CONFIGURATION TERMINÉE!")
    print("="*60)
    print("\n📝 Prochaines étapes:")
    print("1. Démarrez le serveur: python manage.py runserver")
    print("2. Connectez-vous avec: admin / admin123")
    print("3. Accédez au backoffice: http://127.0.0.1:8000/backoffice/fooditems/")
    print("4. Testez les fonctionnalités CRUD!")
    print("\n✨ Bon test!")


if __name__ == '__main__':
    try:
        create_test_data()
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

