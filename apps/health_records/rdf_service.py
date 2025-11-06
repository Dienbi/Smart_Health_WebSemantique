"""
RDF/SPARQL Service for Health Records and Health Metrics
Converts Django models to RDF triples and handles SPARQL operations
"""

from datetime import datetime
from django.conf import settings
from apps.sparql_service.client import SparqlClient
from apps.users.models import User
import logging

logger = logging.getLogger(__name__)

# Namespace prefixes
PREFIX = """
PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
"""


class HealthRecordRDFService:
    """Service for converting HealthRecord to/from RDF and executing SPARQL operations"""
    
    def __init__(self):
        self.client = SparqlClient()
        self.namespace = settings.ONTOLOGY_NAMESPACE
    
    def _get_health_record_uri(self, record_id):
        """Generate URI for a health record"""
        return f"{self.namespace}HealthRecord_{record_id}"
    
    def _get_health_metric_uri(self, metric_id):
        """Generate URI for a health metric"""
        return f"{self.namespace}HealthMetric_{metric_id}"
    
    def _get_user_uri(self, user_id):
        """Generate URI for a user"""
        return f"{self.namespace}User_{user_id}"
    
    def _format_datetime(self, dt):
        """Format datetime to xsd:dateTime format"""
        if dt is None:
            return None
        if isinstance(dt, str):
            return dt
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    def _format_float(self, value):
        """Format float value"""
        if value is None:
            return None
        return float(value)
    
    def create_health_record_rdf(self, record):
        """Convert HealthRecord to RDF triples for INSERT"""
        record_uri = f"<{self.namespace}HealthRecord_{record.health_record_id}>"
        user_id = getattr(record.user, 'user_id', getattr(record.user, 'id', record.user.pk))
        user_uri = f"<{self.namespace}User_{user_id}>"
        
        triples = []
        triples.append(f"{record_uri} rdf:type sh:HealthRecord .")
        triples.append(f"{user_uri} sh:hasHealthRecord {record_uri} .")
        
        # Add properties
        if record.health_record_id:
            triples.append(f"{record_uri} sh:healthRecordId {record.health_record_id} .")
        
        if record.description:
            # Escape quotes in description
            desc = record.description.replace('"', '\\"')
            triples.append(f'{record_uri} sh:healthRecordDescription "{desc}" .')
        
        if record.value is not None:
            # Format float value properly - use string format to avoid issues
            value_str = str(float(record.value))
            triples.append(f'{record_uri} sh:healthRecordValue "{value_str}"^^xsd:float .')
        
        if record.start_date:
            start_date_str = self._format_datetime(record.start_date)
            triples.append(f'{record_uri} sh:healthRecord_startDate "{start_date_str}"^^xsd:dateTime .')
        
        if record.end_date:
            end_date_str = self._format_datetime(record.end_date)
            triples.append(f'{record_uri} sh:healthRecord_endDate "{end_date_str}"^^xsd:dateTime .')
        
        if record.created_at:
            created_at_str = self._format_datetime(record.created_at)
            triples.append(f'{record_uri} sh:healthRecordCreatedAt "{created_at_str}"^^xsd:dateTime .')
        
        # Check if date field exists (for backward compatibility)
        if hasattr(record, 'date') and record.date:
            date_str = self._format_datetime(record.date)
            triples.append(f'{record_uri} sh:healthRecordDate "{date_str}"^^xsd:dateTime .')
        
        # Link to health metric if exists
        if record.health_metric:
            metric_uri = f"<{self.namespace}HealthMetric_{record.health_metric.health_metric_id}>"
            triples.append(f"{record_uri} sh:containsMetric {metric_uri} .")
        
        return "\n".join(triples)
    
    def create_health_metric_rdf(self, metric):
        """Convert HealthMetric to RDF triples for INSERT"""
        metric_uri = f"sh:HealthMetric_{metric.health_metric_id}"
        
        triples = []
        triples.append(f"<{self.namespace}HealthMetric_{metric.health_metric_id}> rdf:type sh:HealthMetric .")
        
        # Add properties
        if metric.health_metric_id:
            triples.append(f"<{self.namespace}HealthMetric_{metric.health_metric_id}> sh:healthMetricId {metric.health_metric_id} .")
        
        if metric.metric_name:
            name = metric.metric_name.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ').replace('\r', ' ')
            triples.append(f'<{self.namespace}HealthMetric_{metric.health_metric_id}> sh:healthMetricName "{name}" .')
        
        if metric.metric_description:
            desc = metric.metric_description.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ').replace('\r', ' ')
            triples.append(f'<{self.namespace}HealthMetric_{metric.health_metric_id}> sh:healthMetricDescription "{desc}" .')
        
        if metric.metric_unit:
            unit = metric.metric_unit.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ').replace('\r', ' ')
            triples.append(f'<{self.namespace}HealthMetric_{metric.health_metric_id}> sh:healthMetricUnit "{unit}" .')
        
        if metric.recorded_at:
            recorded_at_str = self._format_datetime(metric.recorded_at)
            triples.append(f'<{self.namespace}HealthMetric_{metric.health_metric_id}> sh:healthMetricRecordedAt "{recorded_at_str}"^^xsd:dateTime .')
        
        return "\n".join(triples)
    
    def insert_health_record(self, record):
        """Insert a HealthRecord into Fuseki using SPARQL"""
        try:
            triples = self.create_health_record_rdf(record)
            # Format query without extra indentation
            insert_query = f"""{PREFIX}

INSERT DATA {{
{triples}
}}"""
            self.client.execute_update(insert_query)
            logger.info(f"HealthRecord {record.health_record_id} inserted into Fuseki")
            return True
        except Exception as e:
            logger.error(f"Error inserting HealthRecord into Fuseki: {str(e)}")
            raise
    
    def insert_health_metric(self, metric):
        """Insert a HealthMetric into Fuseki using SPARQL"""
        try:
            triples = self.create_health_metric_rdf(metric)
            # Format query without extra indentation
            insert_query = f"""{PREFIX}

INSERT DATA {{
{triples}
}}"""
            self.client.execute_update(insert_query)
            logger.info(f"HealthMetric {metric.health_metric_id} inserted into Fuseki")
            return True
        except Exception as e:
            logger.error(f"Error inserting HealthMetric into Fuseki: {str(e)}")
            raise
    
    def update_health_record(self, record):
        """Update a HealthRecord in Fuseki using SPARQL"""
        try:
            record_uri = f"<{self.namespace}HealthRecord_{record.health_record_id}>"
            
            # First delete all existing triples for this record
            delete_query = f"""{PREFIX}

DELETE {{
    {record_uri} ?p ?o .
    ?user sh:hasHealthRecord {record_uri} .
}}
WHERE {{
    {record_uri} ?p ?o .
    OPTIONAL {{ ?user sh:hasHealthRecord {record_uri} . }}
}}"""
            self.client.execute_update(delete_query)
            
            # Then insert the new triples
            new_triples = self.create_health_record_rdf(record)
            insert_query = f"""{PREFIX}

INSERT DATA {{
{new_triples}
}}"""
            self.client.execute_update(insert_query)
            logger.info(f"HealthRecord {record.health_record_id} updated in Fuseki")
            return True
        except Exception as e:
            logger.error(f"Error updating HealthRecord in Fuseki: {str(e)}")
            raise
    
    def delete_health_record(self, record_id):
        """Delete a HealthRecord from Fuseki using SPARQL"""
        try:
            record_uri = f"<{self.namespace}HealthRecord_{record_id}>"
            
            delete_query = f"""
{PREFIX}

DELETE WHERE {{
    {record_uri} ?p ?o .
    ?user sh:hasHealthRecord {record_uri} .
}}
"""
            self.client.execute_update(delete_query)
            logger.info(f"HealthRecord {record_id} deleted from Fuseki")
            return True
        except Exception as e:
            logger.error(f"Error deleting HealthRecord from Fuseki: {str(e)}")
            raise
    
    def get_health_records_by_user(self, user_id):
        """Get all health records for a user from Fuseki using SPARQL"""
        try:
            user_uri = f"<{self.namespace}User_{user_id}>"
            
            query = f"""
{PREFIX}

SELECT ?record ?recordId ?description ?value ?startDate ?endDate ?createdAt ?date ?metricId ?metricName ?metricUnit
WHERE {{
    {user_uri} sh:hasHealthRecord ?record .
    ?record sh:healthRecordId ?recordId .
    OPTIONAL {{ ?record sh:healthRecordDescription ?description . }}
    OPTIONAL {{ ?record sh:healthRecordValue ?value . }}
    OPTIONAL {{ ?record sh:healthRecord_startDate ?startDate . }}
    OPTIONAL {{ ?record sh:healthRecord_endDate ?endDate . }}
    OPTIONAL {{ ?record sh:healthRecordCreatedAt ?createdAt . }}
    OPTIONAL {{ ?record sh:healthRecordDate ?date . }}
    OPTIONAL {{
        ?record sh:containsMetric ?metric .
        ?metric sh:healthMetricId ?metricId .
        ?metric sh:healthMetricName ?metricName .
        ?metric sh:healthMetricUnit ?metricUnit .
    }}
}}
ORDER BY DESC(?createdAt)
"""
            results = self.client.execute_query(query)
            return self._parse_health_records_results(results)
        except Exception as e:
            logger.error(f"Error getting health records from Fuseki: {str(e)}")
            raise
    
    def get_health_record_by_id(self, record_id):
        """Get a specific health record from Fuseki using SPARQL"""
        try:
            record_uri = f"<{self.namespace}HealthRecord_{record_id}>"
            
            query = f"""
{PREFIX}

SELECT ?recordId ?description ?value ?startDate ?endDate ?createdAt ?date ?userId ?metricId ?metricName ?metricUnit
WHERE {{
    BIND({record_uri} AS ?record) .
    ?record sh:healthRecordId ?recordId .
    OPTIONAL {{ ?record sh:healthRecordDescription ?description . }}
    OPTIONAL {{ ?record sh:healthRecordValue ?value . }}
    OPTIONAL {{ ?record sh:healthRecord_startDate ?startDate . }}
    OPTIONAL {{ ?record sh:healthRecord_endDate ?endDate . }}
    OPTIONAL {{ ?record sh:healthRecordCreatedAt ?createdAt . }}
    OPTIONAL {{ ?record sh:healthRecordDate ?date . }}
    OPTIONAL {{
        ?user sh:hasHealthRecord ?record .
        ?user sh:UserId ?userId .
    }}
    OPTIONAL {{
        ?record sh:containsMetric ?metric .
        ?metric sh:healthMetricId ?metricId .
        ?metric sh:healthMetricName ?metricName .
        ?metric sh:healthMetricUnit ?metricUnit .
    }}
}}
"""
            results = self.client.execute_query(query)
            parsed = self._parse_health_records_results(results)
            return parsed[0] if parsed else None
        except Exception as e:
            logger.error(f"Error getting health record from Fuseki: {str(e)}")
            raise
    
    def get_all_health_metrics(self):
        """Get all health metrics from Fuseki using SPARQL"""
        try:
            query = f"""
{PREFIX}

SELECT ?metricId ?metricName ?metricDescription ?metricUnit ?recordedAt
WHERE {{
    ?metric rdf:type sh:HealthMetric .
    ?metric sh:healthMetricId ?metricId .
    ?metric sh:healthMetricName ?metricName .
    OPTIONAL {{ ?metric sh:healthMetricDescription ?metricDescription . }}
    OPTIONAL {{ ?metric sh:healthMetricUnit ?metricUnit . }}
    OPTIONAL {{ ?metric sh:healthMetricRecordedAt ?recordedAt . }}
}}
ORDER BY ?metricName
"""
            results = self.client.execute_query(query)
            return self._parse_health_metrics_results(results)
        except Exception as e:
            logger.error(f"Error getting health metrics from Fuseki: {str(e)}")
            raise
    
    def _parse_health_records_results(self, results):
        """Parse SPARQL results for health records"""
        records = []
        if 'results' in results and 'bindings' in results['results']:
            for binding in results['results']['bindings']:
                record = {}
                for key, value in binding.items():
                    if 'value' in value:
                        record[key] = value['value']
                records.append(record)
        return records
    
    def _parse_health_metrics_results(self, results):
        """Parse SPARQL results for health metrics"""
        metrics = []
        if 'results' in results and 'bindings' in results['results']:
            for binding in results['results']['bindings']:
                metric = {}
                for key, value in binding.items():
                    if 'value' in value:
                        metric[key] = value['value']
                metrics.append(metric)
        return metrics

