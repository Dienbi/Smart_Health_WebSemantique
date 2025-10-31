from SPARQLWrapper import SPARQLWrapper, JSON
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class SparqlClient:
    """SPARQL Client for Fuseki interactions"""
    
    def __init__(self):
        self.sparql = SPARQLWrapper(settings.FUSEKI_ENDPOINT)
        self.sparql.setReturnFormat(JSON)
        self.update_endpoint = settings.FUSEKI_UPDATE_ENDPOINT
    
    def execute_query(self, query):
        """Execute a SPARQL SELECT query"""
        try:
            self.sparql.setQuery(query)
            results = self.sparql.query().convert()
            return results
        except Exception as e:
            logger.error(f"Error executing SPARQL query: {str(e)}")
            raise
    
    def execute_update(self, update_query):
        """Execute a SPARQL UPDATE query"""
        try:
            update_sparql = SPARQLWrapper(self.update_endpoint)
            update_sparql.setQuery(update_query)
            update_sparql.method = 'POST'
            update_sparql.query()
            return True
        except Exception as e:
            logger.error(f"Error executing SPARQL update: {str(e)}")
            raise
    
    def insert_data(self, triples):
        """Insert RDF triples into the triplestore"""
        insert_query = f"""
        INSERT DATA {{
            {triples}
        }}
        """
        return self.execute_update(insert_query)
    
    def delete_data(self, triples):
        """Delete RDF triples from the triplestore"""
        delete_query = f"""
        DELETE DATA {{
            {triples}
        }}
        """
        return self.execute_update(delete_query)
