"""
Script pour synchroniser les HealthMetric existants de Django vers Fuseki
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smart_Health.settings')
django.setup()

from apps.health_records.models import HealthMetric
from apps.health_records.rdf_service import HealthRecordRDFService
from django.conf import settings

def sync_health_metrics():
    """Synchroniser tous les HealthMetric vers Fuseki"""
    print("=" * 60)
    print("Synchronisation des HealthMetric vers Fuseki")
    print("=" * 60)
    print()
    
    # Get all health metrics from database
    metrics = HealthMetric.objects.all()
    print(f"Nombre de métriques dans la base de données: {metrics.count()}")
    print()
    
    if metrics.count() == 0:
        print("Aucune métrique trouvée dans la base de données.")
        return
    
    rdf_service = HealthRecordRDFService()
    
    success_count = 0
    error_count = 0
    
    for metric in metrics:
        try:
            print(f"Synchronisation de: {metric.metric_name} (ID: {metric.health_metric_id})...", end=" ")
            
            # Insert into Fuseki
            rdf_service.insert_health_metric(metric)
            
            print("[OK]")
            success_count += 1
        except Exception as e:
            print(f"[ERREUR] {str(e)}")
            error_count += 1
    
    print()
    print("=" * 60)
    print(f"Résumé:")
    print(f"  - Synchronisés avec succès: {success_count}")
    print(f"  - Erreurs: {error_count}")
    print("=" * 60)
    
    if success_count > 0:
        print()
        print("✅ Les métriques ont été synchronisées vers Fuseki.")
        print("   Vous pouvez maintenant les interroger via SPARQL.")
    else:
        print()
        print("❌ Aucune métrique n'a pu être synchronisée.")
        print("   Vérifiez que Fuseki est démarré et accessible.")

if __name__ == "__main__":
    try:
        sync_health_metrics()
    except Exception as e:
        import traceback
        print(f"\n❌ Erreur fatale: {str(e)}")
        print(f"\nTraceback:")
        print(traceback.format_exc())

