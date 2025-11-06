"""
Django signals for automatic RDF/Fuseki synchronization - Habits
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Habit, HabitLog
from apps.sparql_service.client import SparqlClient
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Habit)
def sync_habit_to_fuseki(sender, instance, created, **kwargs):
    """Automatically sync Habit to Fuseki when created/updated"""
    try:
        client = SparqlClient()
        
        # Determine habit type class
        habit_type_map = {
            'READING': 'Reading',
            'COOKING': 'Cooking',
            'DRAWING': 'Drawing',
            'JOURNALING': 'Journaling',
            'OTHER': 'Other'  # Use Other class instead of generic Habit
        }
        habit_class = habit_type_map.get(instance.habit_type, 'Habit')
        
        if created:
            # INSERT new habit in Fuseki
            sparql_insert = f"""
            PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
            
            INSERT DATA {{
                sh:Habit_{instance.habit_id} a sh:Habit ;
                    a sh:{habit_class} ;
                    sh:habitId {instance.habit_id} ;
                    sh:habit_name "{instance.habit_name}" ;
                    sh:habit_type "{instance.habit_type}" .
                
                sh:User_{instance.user.user_id} sh:hasHabit sh:Habit_{instance.habit_id} .
            }}
            """
            success = client.execute_update(sparql_insert)
            if success:
                logger.info(f"Habit {instance.habit_id} synced to Fuseki (created)")
        else:
            # UPDATE existing habit in Fuseki
            sparql_update = f"""
            PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
            
            DELETE {{
                sh:Habit_{instance.habit_id} sh:habit_name ?oldName .
                sh:Habit_{instance.habit_id} sh:habit_type ?oldType .
            }}
            INSERT {{
                sh:Habit_{instance.habit_id} sh:habit_name "{instance.habit_name}" .
                sh:Habit_{instance.habit_id} sh:habit_type "{instance.habit_type}" .
            }}
            WHERE {{
                sh:Habit_{instance.habit_id} sh:habit_name ?oldName .
                OPTIONAL {{ sh:Habit_{instance.habit_id} sh:habit_type ?oldType }}
            }}
            """
            success = client.execute_update(sparql_update)
            if success:
                logger.info(f"Habit {instance.habit_id} synced to Fuseki (updated)")
    except Exception as e:
        logger.error(f"Failed to sync Habit {instance.habit_id} to Fuseki: {str(e)}")


@receiver(post_delete, sender=Habit)
def delete_habit_from_fuseki(sender, instance, **kwargs):
    """Automatically delete Habit from Fuseki when deleted from Django"""
    try:
        client = SparqlClient()
        
        sparql_delete = f"""
        PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
        
        DELETE WHERE {{
            sh:Habit_{instance.habit_id} ?p ?o .
        }}
        """
        
        sparql_delete_refs = f"""
        PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
        
        DELETE WHERE {{
            ?s ?p sh:Habit_{instance.habit_id} .
        }}
        """
        
        client.execute_update(sparql_delete)
        client.execute_update(sparql_delete_refs)
        logger.info(f"Habit {instance.habit_id} deleted from Fuseki")
    except Exception as e:
        logger.error(f"Failed to delete Habit {instance.habit_id} from Fuseki: {str(e)}")


@receiver(post_save, sender=HabitLog)
def sync_habitlog_to_fuseki(sender, instance, created, **kwargs):
    """Automatically sync HabitLog to Fuseki when created/updated"""
    try:
        client = SparqlClient()
        
        if created:
            sparql_insert = f"""
            PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
            
            INSERT DATA {{
                sh:HabitLog_{instance.habit_log_id} a sh:HabitLog ;
                    sh:habitLogId {instance.habit_log_id} ;
                    sh:start_date "{instance.start_date.isoformat()}"^^<http://www.w3.org/2001/XMLSchema#dateTime> """
            
            if instance.end_date:
                sparql_insert += f""";
                    sh:end_date "{instance.end_date.isoformat()}"^^<http://www.w3.org/2001/XMLSchema#dateTime> """
            
            if instance.reminder_time:
                sparql_insert += f""";
                    sh:reminder_time "{instance.reminder_time.isoformat()}"^^<http://www.w3.org/2001/XMLSchema#dateTime> """
            
            sparql_insert += f""".
                
                sh:Habit_{instance.habit.habit_id} sh:hasLog sh:HabitLog_{instance.habit_log_id} .
            }}
            """
            
            client.execute_update(sparql_insert)
            logger.info(f"HabitLog {instance.habit_log_id} synced to Fuseki (created)")
    except Exception as e:
        logger.error(f"Failed to sync HabitLog {instance.habit_log_id} to Fuseki: {str(e)}")


@receiver(post_delete, sender=HabitLog)
def delete_habitlog_from_fuseki(sender, instance, **kwargs):
    """Automatically delete HabitLog from Fuseki when deleted from Django"""
    try:
        client = SparqlClient()
        
        sparql_delete = f"""
        PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
        
        DELETE WHERE {{
            sh:HabitLog_{instance.habit_log_id} ?p ?o .
        }}
        """
        
        sparql_delete_refs = f"""
        PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
        
        DELETE WHERE {{
            ?s ?p sh:HabitLog_{instance.habit_log_id} .
        }}
        """
        
        client.execute_update(sparql_delete)
        client.execute_update(sparql_delete_refs)
        logger.info(f"HabitLog {instance.habit_log_id} deleted from Fuseki")
    except Exception as e:
        logger.error(f"Failed to delete HabitLog {instance.habit_log_id} from Fuseki: {str(e)}")
