from django.conf import settings


class SparqlQueryBuilder:
    """Build SPARQL queries from natural language or structured inputs"""
    
    def __init__(self):
        self.namespace = settings.ONTOLOGY_NAMESPACE
        self.prefix = f"PREFIX smarthealth: <{self.namespace}>"
    
    def build_user_query(self, user_id=None):
        """Build query to get user data"""
        query = f"""
        {self.prefix}
        
        SELECT ?user ?name ?email
        WHERE {{
            ?user a smarthealth:User .
            ?user smarthealth:name ?name .
            ?user smarthealth:email ?email .
        """
        
        if user_id:
            query += f"\n    ?user smarthealth:UserId {user_id} ."
        
        query += "\n}"
        return query
    
    def build_activity_query(self, user_id=None):
        """Build query to get activities"""
        query = f"""
        {self.prefix}
        
        SELECT ?activity ?activityName ?description
        WHERE {{
            ?activity a smarthealth:Activity .
            ?activity smarthealth:activity_name ?activityName .
            ?activity smarthealth:activity_description ?description .
        }}
        """
        return query
    
    def build_activity_log_query(self, user_id):
        """Build query to get activity logs for a user"""
        query = f"""
        {self.prefix}
        
        SELECT ?log ?activity ?date ?duration
        WHERE {{
            ?user a smarthealth:User .
            ?user smarthealth:UserId {user_id} .
            ?user smarthealth:PerformsActivity ?log .
            ?log smarthealth:dateActivityLog ?date .
            ?log smarthealth:duration ?duration .
        }}
        """
        return query
    
    def build_health_metrics_query(self, user_id):
        """Build query to get health metrics for a user"""
        query = f"""
        {self.prefix}
        
        SELECT ?metric ?metricName ?metricValue ?metricUnit
        WHERE {{
            ?user a smarthealth:User .
            ?user smarthealth:UserId {user_id} .
            ?user smarthealth:hasHealthRecord ?record .
            ?record smarthealth:containsMetric ?metric .
            ?metric smarthealth:healthMetricName ?metricName .
            ?metric smarthealth:healthMetricValue ?metricValue .
            ?metric smarthealth:healthMetricUnit ?metricUnit .
        }}
        """
        return query
    
    def build_meal_query(self, user_id):
        """Build query to get meals for a user"""
        query = f"""
        {self.prefix}
        
        SELECT ?meal ?mealName ?calories
        WHERE {{
            ?user a smarthealth:User .
            ?user smarthealth:UserId {user_id} .
            ?user smarthealth:hasMeal ?meal .
            ?meal smarthealth:name_meal ?mealName .
            ?meal smarthealth:calories_total ?calories .
        }}
        """
        return query
    
    def build_habit_query(self, user_id):
        """Build query to get habits for a user"""
        query = f"""
        {self.prefix}
        
        SELECT ?habit ?habitName ?habitType
        WHERE {{
            ?user a smarthealth:User .
            ?user smarthealth:UserId {user_id} .
            ?user smarthealth:hashabit ?habit .
            ?habit smarthealth:habbit-name ?habitName .
            ?habit smarthealth:type ?habitType .
        }}
        """
        return query
    
    def build_defi_query(self):
        """Build query to get all challenges"""
        query = f"""
        {self.prefix}
        
        SELECT ?defi ?defiName ?defiDescription
        WHERE {{
            ?defi a smarthealth:Defi .
            ?defi smarthealth:defiName ?defiName .
            ?defi smarthealth:defiDescription ?defiDescription .
        }}
        """
        return query
    
    def build_participation_query(self, user_id):
        """Build query to get participations for a user"""
        query = f"""
        {self.prefix}
        
        SELECT ?participation ?defi ?startDate ?endDate
        WHERE {{
            ?user a smarthealth:User .
            ?user smarthealth:UserId {user_id} .
            ?user smarthealth:hasParticipation ?participation .
            ?participation smarthealth:start_date ?startDate .
            OPTIONAL {{ ?participation smarthealth:end_Date ?endDate . }}
        }}
        """
        return query
    
    def build_custom_query(self, select_vars, where_clause):
        """Build a custom SPARQL query"""
        query = f"""
        {self.prefix}
        
        SELECT {select_vars}
        WHERE {{
            {where_clause}
        }}
        """
        return query
