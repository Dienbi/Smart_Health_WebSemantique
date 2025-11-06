class SparqlResultFormatter:
    """Format SPARQL query results"""
    
    @staticmethod
    def format_results(results):
        """Format raw SPARQL results to Python dict"""
        formatted = []
        
        # Handle empty or None results
        if not results:
            return formatted
        
        # Handle different result formats
        if isinstance(results, dict):
            if 'results' in results and 'bindings' in results['results']:
                for binding in results['results']['bindings']:
                    formatted_row = {}
                    for key, value in binding.items():
                        if isinstance(value, dict):
                            formatted_row[key] = value.get('value', '')
                        else:
                            formatted_row[key] = value
                    formatted.append(formatted_row)
            elif 'bindings' in results:
                # Direct bindings format
                for binding in results['bindings']:
                    formatted_row = {}
                    for key, value in binding.items():
                        if isinstance(value, dict):
                            formatted_row[key] = value.get('value', '')
                        else:
                            formatted_row[key] = value
                    formatted.append(formatted_row)
        elif isinstance(results, list):
            # Already a list format
            formatted = results
        
        return formatted
    
    @staticmethod
    def format_user_results(results):
        """Format user query results"""
        users = []
        for result in SparqlResultFormatter.format_results(results):
            users.append({
                'uri': result.get('user', ''),
                'name': result.get('name', ''),
                'email': result.get('email', '')
            })
        return users
    
    @staticmethod
    def format_activity_results(results):
        """Format activity query results"""
        activities = []
        for result in SparqlResultFormatter.format_results(results):
            activities.append({
                'uri': result.get('activity', ''),
                'name': result.get('activityName', ''),
                'description': result.get('description', '')
            })
        return activities
    
    @staticmethod
    def format_health_metric_results(results):
        """Format health metric query results"""
        metrics = []
        for result in SparqlResultFormatter.format_results(results):
            metrics.append({
                'uri': result.get('metric', ''),
                'name': result.get('metricName', ''),
                'value': result.get('metricValue', ''),
                'unit': result.get('metricUnit', '')
            })
        return metrics
    
    @staticmethod
    def format_meal_results(results):
        """Format meal query results"""
        meals = []
        for result in SparqlResultFormatter.format_results(results):
            meals.append({
                'uri': result.get('meal', ''),
                'name': result.get('mealName', ''),
                'calories': result.get('calories', '')
            })
        return meals
    
    @staticmethod
    def format_habit_results(results):
        """Format habit query results"""
        habits = []
        for result in SparqlResultFormatter.format_results(results):
            habits.append({
                'uri': result.get('habit', ''),
                'name': result.get('habitName', ''),
                'type': result.get('habitType', '')
            })
        return habits
    
    @staticmethod
    def format_defi_results(results):
        """Format defi query results"""
        defis = []
        for result in SparqlResultFormatter.format_results(results):
            defis.append({
                'uri': result.get('defi', ''),
                'name': result.get('defiName', ''),
                'description': result.get('defiDescription', '')
            })
        return defis
    
    @staticmethod
    def format_to_json(results):
        """Convert SPARQL results to clean JSON format"""
        return {
            'count': len(results) if isinstance(results, list) else 0,
            'results': results
        }
