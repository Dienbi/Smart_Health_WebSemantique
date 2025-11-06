"""
Signals for Defi model to sync with Fuseki RDF store
"""
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.defis.models import Defi
from apps.sparql_service.client import SparqlClient

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Defi)
def sync_defi_to_fuseki(sender, instance, created, **kwargs):
    """
    Sync Defi to Fuseki when created or updated
    """
    try:
        client = SparqlClient()
        
        if created:
            # INSERT new defi
            sparql = f"""
PREFIX sh: <http://dhia.org/ontologies/smarthealth#>

INSERT DATA {{
    sh:Defi_{instance.defi_id} a sh:Defi ;
        sh:defi_name "{instance.defi_name}" ;
        sh:defi_description "{instance.defi_description}" ;
        sh:defi_id {instance.defi_id} .
}}
"""
            logger.info(f"Syncing new Defi to Fuseki: {instance.defi_name}")
        else:
            # UPDATE existing defi (DELETE then INSERT)
            sparql = f"""
PREFIX sh: <http://dhia.org/ontologies/smarthealth#>

DELETE {{
    sh:Defi_{instance.defi_id} sh:defi_name ?name ;
        sh:defi_description ?desc .
}}
INSERT {{
    sh:Defi_{instance.defi_id} sh:defi_name "{instance.defi_name}" ;
        sh:defi_description "{instance.defi_description}" .
}}
WHERE {{
    sh:Defi_{instance.defi_id} a sh:Defi .
    OPTIONAL {{ sh:Defi_{instance.defi_id} sh:defi_name ?name }}
    OPTIONAL {{ sh:Defi_{instance.defi_id} sh:defi_description ?desc }}
}}
"""
            logger.info(f"Updating Defi in Fuseki: {instance.defi_name}")
        
        client.execute_update(sparql)
        logger.info(f"✅ Defi '{instance.defi_name}' synced to Fuseki")
        
    except Exception as e:
        logger.error(f"❌ Error syncing Defi to Fuseki: {str(e)}")


@receiver(post_delete, sender=Defi)
def delete_defi_from_fuseki(sender, instance, **kwargs):
    """
    Delete Defi from Fuseki when deleted from Django
    """
    try:
        client = SparqlClient()
        
        sparql = f"""
PREFIX sh: <http://dhia.org/ontologies/smarthealth#>

DELETE WHERE {{
    sh:Defi_{instance.defi_id} ?p ?o .
}}
"""
        
        client.execute_update(sparql)
        logger.info(f"✅ Defi '{instance.defi_name}' deleted from Fuseki")
        
    except Exception as e:
        logger.error(f"❌ Error deleting Defi from Fuseki: {str(e)}")
