"""
Import ontology data from the TTL file to Fuseki server
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smart_Health.settings')
django.setup()

from django.conf import settings
from rdflib import Graph
from apps.sparql_service.client import SparqlClient


def load_ontology():
    """Load the ontology from TTL file"""
    ontology_path = settings.ONTOLOGY_FILE
    
    if not ontology_path.exists():
        print(f"❌ Error: Ontology file not found at {ontology_path}")
        return None
    
    print(f"📖 Loading ontology from: {ontology_path}")
    
    try:
        g = Graph()
        g.parse(ontology_path, format='turtle')
        print(f"✅ Ontology loaded successfully! ({len(g)} triples)")
        return g
    except Exception as e:
        print(f"❌ Error loading ontology: {str(e)}")
        return None


def upload_to_fuseki(graph):
    """Upload the ontology to Fuseki"""
    if not graph:
        return False
    
    print("\n📤 Uploading ontology to Fuseki...")
    print(f"Fuseki endpoint: {settings.FUSEKI_UPDATE_ENDPOINT}")
    
    try:
        client = SparqlClient()
        
        # Convert graph to N-Triples format for upload
        triples = graph.serialize(format='nt')
        
        # Insert data
        client.insert_data(triples)
        
        print("✅ Ontology uploaded successfully to Fuseki!")
        return True
    
    except Exception as e:
        print(f"❌ Error uploading to Fuseki: {str(e)}")
        print("\nMake sure:")
        print("1. Fuseki server is running")
        print("2. Dataset 'smarthealth' exists")
        print("3. Update permissions are enabled")
        return False


def main():
    """Main function"""
    print("\n" + "="*60)
    print("🔄 Import Ontology to Fuseki")
    print("="*60 + "\n")
    
    # Load ontology
    graph = load_ontology()
    
    if graph:
        # Upload to Fuseki
        upload_to_fuseki(graph)
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
