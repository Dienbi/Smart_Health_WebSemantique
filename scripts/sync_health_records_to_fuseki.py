"""
Script pour synchroniser les HealthRecord existants de Django vers Fuseki
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smart_Health.settings')
django.setup()

from apps.health_records.models import HealthRecord
from apps.health_records.rdf_service import HealthRecordRDFService
from django.conf import settings

def sync_health_records():
    """Synchroniser tous les HealthRecord vers Fuseki"""
    print("=" * 60)
    print("Synchronisation des HealthRecord vers Fuseki")
    print("=" * 60)
    print()
    
    # Get all health records from database
    records = HealthRecord.objects.select_related('user', 'health_metric').all()
    print(f"Nombre de health records dans la base de donnees: {records.count()}")
    print()
    
    if records.count() == 0:
        print("Aucun health record trouve dans la base de donnees.")
        return
    
    rdf_service = HealthRecordRDFService()
    
    success_count = 0
    error_count = 0
    
    for record in records:
        try:
            print(f"Synchronisation de: HealthRecord ID {record.health_record_id} (User: {record.user.username})...", end=" ")
            
            # Insert into Fuseki
            rdf_service.insert_health_record(record)
            
            print("[OK]")
            success_count += 1
        except Exception as e:
            print(f"[ERREUR] {str(e)}")
            error_count += 1
    
    print()
    print("=" * 60)
    print(f"Resume:")
    print(f"  - Synchronises avec succes: {success_count}")
    print(f"  - Erreurs: {error_count}")
    print("=" * 60)
    
    if success_count > 0:
        print()
        print("OK Les health records ont ete synchronises vers Fuseki.")
        print("   Vous pouvez maintenant les interroger via SPARQL.")
    else:
        print()
        print("ERREUR Aucun health record n'a pu etre synchronise.")
        print("   Verifiez que Fuseki est demarre et accessible.")

if __name__ == "__main__":
    try:
        sync_health_records()
    except Exception as e:
        import traceback
        print(f"\nERREUR Erreur fatale: {str(e)}")
        print(f"\nTraceback:")
        print(traceback.format_exc())

