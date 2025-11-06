"""Test query for health metrics from Fuseki"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smart_Health.settings')
django.setup()

from apps.health_records.rdf_service import HealthRecordRDFService

rdf = HealthRecordRDFService()
results = rdf.get_all_health_metrics()
print(f'Nombre de metriques trouvees: {len(results)}')
for r in results:
    print(f"  - {r.get('metricName', 'N/A')} (ID: {r.get('metricId', 'N/A')})")

