"""
Commande Django pour synchroniser les données existantes vers RDF
Usage: python manage.py sync_rdf
"""

from django.core.management.base import BaseCommand
from apps.meals.models import Meal, FoodItem
from apps.meals.rdf_manager import rdf_manager


class Command(BaseCommand):
    help = 'Synchronise les données Django existantes vers l\'ontologie RDF'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force la resynchronisation complète (supprime et recrée)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('[START] Debut de la synchronisation RDF...'))
        
        force = options.get('force', False)
        
        # Synchroniser les FoodItems
        self.stdout.write('\n[FOODITEMS] Synchronisation des FoodItems...')
        fooditems = FoodItem.objects.all().prefetch_related('calories', 'protein', 'carbs', 'fiber', 'sugar')
        
        for item in fooditems:
            try:
                # Récupérer les valeurs nutritionnelles
                calories = getattr(item.calories, 'calories_value', None) if hasattr(item, 'calories') else None
                protein = getattr(item.protein, 'protein_value', None) if hasattr(item, 'protein') else None
                carbs = getattr(item.carbs, 'carbs_value', None) if hasattr(item, 'carbs') else None
                fiber = getattr(item.fiber, 'fiber_value', None) if hasattr(item, 'fiber') else None
                sugar = getattr(item.sugar, 'sugar_value', None) if hasattr(item, 'sugar') else None
                
                # Vérifier si existe déjà en RDF
                existing = rdf_manager.get_fooditem(item.food_item_id)
                
                if existing and not force:
                    self.stdout.write(f'  [SKIP] FoodItem {item.food_item_id} deja en RDF')
                else:
                    if existing and force:
                        rdf_manager.delete_fooditem(item.food_item_id)
                    
                    rdf_manager.create_fooditem(
                        fooditem_id=item.food_item_id,
                        name=item.food_item_name,
                        description=item.food_item_description,
                        food_type=item.food_type,
                        calories=calories,
                        protein=protein,
                        carbs=carbs,
                        fiber=fiber,
                        sugar=sugar
                    )
                    self.stdout.write(self.style.SUCCESS(f'  [OK] FoodItem synchronise : {item.food_item_name}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  [ERROR] Erreur pour {item.food_item_name} : {e}'))
        
        # Synchroniser les Meals
        self.stdout.write('\n[MEALS] Synchronisation des Meals...')
        meals = Meal.objects.all().select_related('user').prefetch_related('food_items')
        
        for meal in meals:
            try:
                # Vérifier si existe déjà en RDF
                existing = rdf_manager.get_meal(meal.meal_id)
                
                if existing and not force:
                    self.stdout.write(f'  [SKIP] Meal {meal.meal_id} deja en RDF')
                else:
                    if existing and force:
                        rdf_manager.delete_meal(meal.meal_id)
                    
                    rdf_manager.create_meal(
                        meal_id=meal.meal_id,
                        meal_name=meal.meal_name,
                        meal_type=meal.meal_type,
                        total_calories=meal.total_calories,
                        meal_date=meal.meal_date,
                        user_id=meal.user.user_id
                    )
                    
                    # Lier les food items
                    for food_item in meal.food_items.all():
                        rdf_manager.link_fooditem_to_meal(meal.meal_id, food_item.food_item_id)
                    
                    self.stdout.write(self.style.SUCCESS(f'  [OK] Meal synchronise : {meal.meal_name}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  [ERROR] Erreur pour {meal.meal_name} : {e}'))
        
        # Afficher les statistiques
        stats = rdf_manager.get_stats()
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('\n[STATS] STATISTIQUES RDF :'))
        self.stdout.write(f"  Total triplets: {stats['total_triples']}")
        self.stdout.write(f"  Total Meals: {stats['total_meals']}")
        self.stdout.write(f"  Total FoodItems: {stats['total_fooditems']}")
        self.stdout.write('='*50 + '\n')
        
        self.stdout.write(self.style.SUCCESS('[DONE] Synchronisation terminee avec succes !'))

