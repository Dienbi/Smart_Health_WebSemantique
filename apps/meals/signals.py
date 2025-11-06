"""
Django signals for automatic RDF/Fuseki synchronization - Meals
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Meal, FoodItem
from apps.sparql_service.client import SparqlClient
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Meal)
def sync_meal_to_fuseki(sender, instance, created, **kwargs):
    """Automatically sync Meal to Fuseki when created/updated"""
    try:
        client = SparqlClient()
        
        # Determine meal type class
        meal_type_map = {
            'BREAKFAST': 'Breakfast',
            'LUNCH': 'Lunch',
            'DINNER': 'Dinner',
            'SNACK': 'Snack'
        }
        meal_class = meal_type_map.get(instance.meal_type, 'Meal')
        
        if created:
            # INSERT new meal in Fuseki
            sparql_insert = f"""
            PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
            
            INSERT DATA {{
                sh:Meal_{instance.meal_id} a sh:Meal ;
                    a sh:{meal_class} ;
                    sh:mealId {instance.meal_id} ;
                    sh:meal_name "{instance.meal_name}" ;
                    sh:meal_type "{instance.meal_type}" ;
                    sh:total_calories {instance.total_calories} ;
                    sh:meal_date "{instance.meal_date.isoformat()}"^^<http://www.w3.org/2001/XMLSchema#dateTime> .
                
                sh:User_{instance.user.user_id} sh:hasMeal sh:Meal_{instance.meal_id} .
            }}
            """
            success = client.execute_update(sparql_insert)
            if success:
                logger.info(f"Meal {instance.meal_id} synced to Fuseki (created)")
            else:
                logger.error(f"Failed to sync Meal {instance.meal_id} to Fuseki")
        else:
            # UPDATE existing meal in Fuseki
            sparql_update = f"""
            PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
            
            DELETE {{
                sh:Meal_{instance.meal_id} sh:meal_name ?oldName .
                sh:Meal_{instance.meal_id} sh:total_calories ?oldCalories .
                sh:Meal_{instance.meal_id} sh:meal_date ?oldDate .
            }}
            INSERT {{
                sh:Meal_{instance.meal_id} sh:meal_name "{instance.meal_name}" .
                sh:Meal_{instance.meal_id} sh:total_calories {instance.total_calories} .
                sh:Meal_{instance.meal_id} sh:meal_date "{instance.meal_date.isoformat()}"^^<http://www.w3.org/2001/XMLSchema#dateTime> .
            }}
            WHERE {{
                sh:Meal_{instance.meal_id} sh:meal_name ?oldName .
                OPTIONAL {{ sh:Meal_{instance.meal_id} sh:total_calories ?oldCalories }}
                OPTIONAL {{ sh:Meal_{instance.meal_id} sh:meal_date ?oldDate }}
            }}
            """
            success = client.execute_update(sparql_update)
            if success:
                logger.info(f"Meal {instance.meal_id} synced to Fuseki (updated)")
            else:
                logger.error(f"Failed to sync Meal {instance.meal_id} to Fuseki")
    except Exception as e:
        logger.error(f"Failed to sync Meal {instance.meal_id} to Fuseki: {str(e)}")
        # Don't raise - allow Django operation to continue


@receiver(post_delete, sender=Meal)
def delete_meal_from_fuseki(sender, instance, **kwargs):
    """Automatically delete Meal from Fuseki when deleted from Django"""
    try:
        client = SparqlClient()
        
        sparql_delete = f"""
        PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
        
        DELETE WHERE {{
            sh:Meal_{instance.meal_id} ?p ?o .
        }}
        """
        
        # Also remove references to this meal
        sparql_delete_refs = f"""
        PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
        
        DELETE WHERE {{
            ?s ?p sh:Meal_{instance.meal_id} .
        }}
        """
        
        success1 = client.execute_update(sparql_delete)
        success2 = client.execute_update(sparql_delete_refs)
        
        if success1 and success2:
            logger.info(f"Meal {instance.meal_id} deleted from Fuseki")
        else:
            logger.error(f"Failed to delete Meal {instance.meal_id} from Fuseki")
    except Exception as e:
        logger.error(f"Failed to delete Meal {instance.meal_id} from Fuseki: {str(e)}")
        # Don't raise - allow Django operation to continue


@receiver(post_save, sender=FoodItem)
def sync_fooditem_to_fuseki(sender, instance, created, **kwargs):
    """Automatically sync FoodItem to Fuseki when created/updated"""
    try:
        client = SparqlClient()
        
        if created:
            # INSERT new food item in Fuseki
            sparql_insert = f"""
            PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
            
            INSERT DATA {{
                sh:FoodItem_{instance.food_item_id} a sh:FoodItem ;
                    sh:foodItemId {instance.food_item_id} ;
                    sh:foodItemName "{instance.food_item_name}" ;
                    sh:foodItemDescription "{instance.food_item_description}" ;
                    sh:food_type "{instance.food_type}" .
            """
            
            # Add meal relationship if exists
            if instance.meal:
                sparql_insert += f"""
                sh:Meal_{instance.meal.meal_id} sh:hasFoodItem sh:FoodItem_{instance.food_item_id} .
            """
            
            sparql_insert += "}"
            
            success = client.execute_update(sparql_insert)
            if success:
                logger.info(f"FoodItem {instance.food_item_id} synced to Fuseki (created)")
            else:
                logger.error(f"Failed to sync FoodItem {instance.food_item_id} to Fuseki")
        else:
            # UPDATE existing food item in Fuseki
            sparql_update = f"""
            PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
            
            DELETE {{
                sh:FoodItem_{instance.food_item_id} sh:foodItemName ?oldName .
                sh:FoodItem_{instance.food_item_id} sh:foodItemDescription ?oldDesc .
                sh:FoodItem_{instance.food_item_id} sh:food_type ?oldType .
            }}
            INSERT {{
                sh:FoodItem_{instance.food_item_id} sh:foodItemName "{instance.food_item_name}" .
                sh:FoodItem_{instance.food_item_id} sh:foodItemDescription "{instance.food_item_description}" .
                sh:FoodItem_{instance.food_item_id} sh:food_type "{instance.food_type}" .
            }}
            WHERE {{
                sh:FoodItem_{instance.food_item_id} sh:foodItemName ?oldName .
                OPTIONAL {{ sh:FoodItem_{instance.food_item_id} sh:foodItemDescription ?oldDesc }}
                OPTIONAL {{ sh:FoodItem_{instance.food_item_id} sh:food_type ?oldType }}
            }}
            """
            success = client.execute_update(sparql_update)
            if success:
                logger.info(f"FoodItem {instance.food_item_id} synced to Fuseki (updated)")
            else:
                logger.error(f"Failed to sync FoodItem {instance.food_item_id} to Fuseki")
    except Exception as e:
        logger.error(f"Failed to sync FoodItem {instance.food_item_id} to Fuseki: {str(e)}")
        # Don't raise - allow Django operation to continue


@receiver(post_delete, sender=FoodItem)
def delete_fooditem_from_fuseki(sender, instance, **kwargs):
    """Automatically delete FoodItem from Fuseki when deleted from Django"""
    try:
        client = SparqlClient()
        
        sparql_delete = f"""
        PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
        
        DELETE WHERE {{
            sh:FoodItem_{instance.food_item_id} ?p ?o .
        }}
        """
        
        # Also remove references to this food item
        sparql_delete_refs = f"""
        PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
        
        DELETE WHERE {{
            ?s ?p sh:FoodItem_{instance.food_item_id} .
        }}
        """
        
        success1 = client.execute_update(sparql_delete)
        success2 = client.execute_update(sparql_delete_refs)
        
        if success1 and success2:
            logger.info(f"FoodItem {instance.food_item_id} deleted from Fuseki")
        else:
            logger.error(f"Failed to delete FoodItem {instance.food_item_id} from Fuseki")
    except Exception as e:
        logger.error(f"Failed to delete FoodItem {instance.food_item_id} from Fuseki: {str(e)}")
        # Don't raise - allow Django operation to continue
