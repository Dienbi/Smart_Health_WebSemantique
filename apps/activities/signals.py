"""
Django signals for automatic RDF/Fuseki synchronization - Activities
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Activity, ActivityLog, Cardio, Musculation, Natation
from apps.sparql_service.client import SparqlClient
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Activity)
def sync_activity_to_fuseki(sender, instance, created, **kwargs):
    """Automatically sync Activity to Fuseki when created/updated"""
    try:
        client = SparqlClient()
        
        # Determine activity type
        activity_type = 'Activity'
        if hasattr(instance, 'cardio_details'):
            activity_type = 'Cardio'
        elif hasattr(instance, 'musculation_details'):
            activity_type = 'Musculation'
        elif hasattr(instance, 'natation_details'):
            activity_type = 'Natation'
        
        if created:
            # INSERT new activity in Fuseki
            sparql_insert = f"""
            PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
            
            INSERT DATA {{
                sh:Activity_{instance.activity_id} a sh:Activity ;
                    a sh:{activity_type} ;
                    sh:activityId {instance.activity_id} ;
                    sh:activity_name "{instance.activity_name}" ;
                    sh:activity_description "{instance.activity_description}" .
            }}
            """
            success = client.execute_update(sparql_insert)
            if success:
                logger.info(f"Activity {instance.activity_id} synced to Fuseki (created)")
        else:
            # UPDATE existing activity in Fuseki
            sparql_update = f"""
            PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
            
            DELETE {{
                sh:Activity_{instance.activity_id} sh:activity_name ?oldName .
                sh:Activity_{instance.activity_id} sh:activity_description ?oldDesc .
            }}
            INSERT {{
                sh:Activity_{instance.activity_id} sh:activity_name "{instance.activity_name}" .
                sh:Activity_{instance.activity_id} sh:activity_description "{instance.activity_description}" .
            }}
            WHERE {{
                sh:Activity_{instance.activity_id} sh:activity_name ?oldName .
                OPTIONAL {{ sh:Activity_{instance.activity_id} sh:activity_description ?oldDesc }}
            }}
            """
            success = client.execute_update(sparql_update)
            if success:
                logger.info(f"Activity {instance.activity_id} synced to Fuseki (updated)")
    except Exception as e:
        logger.error(f"Failed to sync Activity {instance.activity_id} to Fuseki: {str(e)}")


@receiver(post_delete, sender=Activity)
def delete_activity_from_fuseki(sender, instance, **kwargs):
    """Automatically delete Activity from Fuseki when deleted from Django"""
    try:
        client = SparqlClient()
        
        sparql_delete = f"""
        PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
        
        DELETE WHERE {{
            sh:Activity_{instance.activity_id} ?p ?o .
        }}
        """
        
        sparql_delete_refs = f"""
        PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
        
        DELETE WHERE {{
            ?s ?p sh:Activity_{instance.activity_id} .
        }}
        """
        
        client.execute_update(sparql_delete)
        client.execute_update(sparql_delete_refs)
        logger.info(f"Activity {instance.activity_id} deleted from Fuseki")
    except Exception as e:
        logger.error(f"Failed to delete Activity {instance.activity_id} from Fuseki: {str(e)}")


@receiver(post_save, sender=ActivityLog)
def sync_activitylog_to_fuseki(sender, instance, created, **kwargs):
    """Automatically sync ActivityLog to Fuseki when created/updated"""
    try:
        client = SparqlClient()
        
        if created:
            sparql_insert = f"""
            PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
            
            INSERT DATA {{
                sh:ActivityLog_{instance.activity_log_id} a sh:ActivityLog ;
                    sh:activityLogId {instance.activity_log_id} ;
                    sh:duration {instance.duration} ;
                    sh:date "{instance.date.isoformat()}"^^<http://www.w3.org/2001/XMLSchema#dateTime> """
            
            if instance.intensity:
                sparql_insert += f""";
                    sh:intensity "{instance.intensity}" """
            
            sparql_insert += f""".
                
                sh:User_{instance.user.user_id} sh:CreatesActivityLog sh:ActivityLog_{instance.activity_log_id} .
                sh:ActivityLog_{instance.activity_log_id} sh:logsActivity sh:Activity_{instance.activity.activity_id} .
            }}
            """
            
            client.execute_update(sparql_insert)
            logger.info(f"ActivityLog {instance.activity_log_id} synced to Fuseki (created)")
    except Exception as e:
        logger.error(f"Failed to sync ActivityLog {instance.activity_log_id} to Fuseki: {str(e)}")


@receiver(post_delete, sender=ActivityLog)
def delete_activitylog_from_fuseki(sender, instance, **kwargs):
    """Automatically delete ActivityLog from Fuseki when deleted from Django"""
    try:
        client = SparqlClient()
        
        sparql_delete = f"""
        PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
        
        DELETE WHERE {{
            sh:ActivityLog_{instance.activity_log_id} ?p ?o .
        }}
        """
        
        sparql_delete_refs = f"""
        PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
        
        DELETE WHERE {{
            ?s ?p sh:ActivityLog_{instance.activity_log_id} .
        }}
        """
        
        client.execute_update(sparql_delete)
        client.execute_update(sparql_delete_refs)
        logger.info(f"ActivityLog {instance.activity_log_id} deleted from Fuseki")
    except Exception as e:
        logger.error(f"Failed to delete ActivityLog {instance.activity_log_id} from Fuseki: {str(e)}")
