"""
Django signals for automatic RDF/SPARQL synchronization
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import HealthRecord, HealthMetric
from .rdf_service import HealthRecordRDFService
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=HealthRecord)
def sync_health_record_to_fuseki(sender, instance, created, **kwargs):
    """Automatically sync HealthRecord to Fuseki when created/updated"""
    try:
        rdf_service = HealthRecordRDFService()
        if created:
            rdf_service.insert_health_record(instance)
            logger.info(f"HealthRecord {instance.health_record_id} synced to Fuseki (created)")
        else:
            rdf_service.update_health_record(instance)
            logger.info(f"HealthRecord {instance.health_record_id} synced to Fuseki (updated)")
    except Exception as e:
        logger.error(f"Failed to sync HealthRecord {instance.health_record_id} to Fuseki: {str(e)}")
        # Don't raise - allow Django operation to continue


@receiver(post_delete, sender=HealthRecord)
def delete_health_record_from_fuseki(sender, instance, **kwargs):
    """Automatically delete HealthRecord from Fuseki when deleted from Django"""
    try:
        rdf_service = HealthRecordRDFService()
        rdf_service.delete_health_record(instance.health_record_id)
        logger.info(f"HealthRecord {instance.health_record_id} deleted from Fuseki")
    except Exception as e:
        logger.error(f"Failed to delete HealthRecord {instance.health_record_id} from Fuseki: {str(e)}")
        # Don't raise - allow Django operation to continue


@receiver(post_save, sender=HealthMetric)
def sync_health_metric_to_fuseki(sender, instance, created, **kwargs):
    """Automatically sync HealthMetric to Fuseki when created/updated"""
    try:
        rdf_service = HealthRecordRDFService()
        if created:
            rdf_service.insert_health_metric(instance)
            logger.info(f"HealthMetric {instance.health_metric_id} synced to Fuseki (created)")
        else:
            # For updates, delete and reinsert
            rdf_service.insert_health_metric(instance)
            logger.info(f"HealthMetric {instance.health_metric_id} synced to Fuseki (updated)")
    except Exception as e:
        logger.error(f"Failed to sync HealthMetric {instance.health_metric_id} to Fuseki: {str(e)}")
        # Don't raise - allow Django operation to continue

