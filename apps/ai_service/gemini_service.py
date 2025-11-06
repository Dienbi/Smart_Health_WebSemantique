"""
Real AI-powered prompt to SPARQL converter using Google Gemini
"""

import requests
from django.conf import settings
import os
import json


class GeminiAIService:
    """Use Google Gemini AI to convert natural language to SPARQL"""
    
    def __init__(self):
        # Get API key from environment or settings
        self.api_key = os.getenv('GEMINI_API_KEY', '')
        self.enabled = bool(self.api_key)
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        
        # Try to find an available model
        if self.enabled:
            self.model_name = self._find_available_model()
            self.api_url = f"{self.base_url}/models/{self.model_name}:generateContent"
        else:
            self.model_name = None
            self.api_url = None
    
    def _find_available_model(self):
        """Try to find an available Gemini model"""
        # List of models to try in order (avoid experimental models)
        models_to_try = [
            "gemini-1.5-flash-latest",
            "gemini-1.5-flash",
            "gemini-1.5-pro-latest", 
            "gemini-1.5-pro",
            "gemini-pro",
            "gemini-1.0-pro"
        ]
        
        # Try to list available models
        try:
            response = requests.get(
                f"{self.base_url}/models?key={self.api_key}",
                timeout=5
            )
            if response.status_code == 200:
                models_data = response.json().get('models', [])
                for model in models_data:
                    if 'generateContent' in model.get('supportedGenerationMethods', []):
                        model_name = model['name'].replace('models/', '')
                        # Skip experimental models that might have quota issues
                        if '-exp' not in model_name and '2.5' not in model_name:
                            return model_name
                # If no stable model found, use first available
                for model in models_data:
                    if 'generateContent' in model.get('supportedGenerationMethods', []):
                        return model['name'].replace('models/', '')
        except Exception:
            pass
        
        # Fallback to trying models in order
        return models_to_try[0]
    
    def generate_sparql(self, prompt, user_id=None):
        """
        Use Gemini AI to generate SPARQL query from natural language
        """
        if not self.enabled:
            return None, "AI service not configured. Add GEMINI_API_KEY to .env file"
        
        # Build the AI prompt with context
        ontology_context = f"""
You are a SPARQL query expert. Convert natural language questions to SPARQL queries.

**Ontology Context:**
- Namespace: <http://dhia.org/ontologies/smarthealth#>
- Prefix: PREFIX sh: <http://dhia.org/ontologies/smarthealth#>

**Available Classes:**
- sh:User (properties: username, email)
- sh:Student (subclass of User, property: classe)
- sh:Teacher (subclass of User, property: matier)
- sh:Activity (has subclasses: Cardio, Musculation, Natation)
- sh:ActivityLog (properties: duration, intensity, date)
- sh:HealthRecord (properties: recordDate)
- sh:HealthMetric (has subclasses: HeartRate, Cholesterol, SugarLevel, Oxygen, Weight, Height)
  - Properties: healthMetricId (integer), healthMetricName (string), healthMetricDescription (string), healthMetricUnit (string), healthMetricRecordedAt (dateTime)
  - IMPORTANT: For DELETE/UPDATE operations on HealthMetric, use healthMetricName (string) to identify metrics, NOT healthMetricId (integer)
- sh:Meal (has subclasses: Breakfast, Lunch, Dinner, Snack) - IMPORTANT: Query for specific types
- sh:FoodItem (properties: name, calories, protein, carbs)
- sh:Habit (has subclasses: Reading, Cooking, Drawing, Journaling)
- sh:HabitLog (properties: frequency, notes)
- sh:Defi (Challenge/Competition)
- sh:Participation (properties: progress, status)

**Object Properties:**
- sh:hasHealthRecord (User -> HealthRecord)
- sh:containsMetric (HealthRecord -> HealthMetric)
- sh:PerformsActivity (User -> Activity)
- sh:CreatesActivityLog (User -> ActivityLog)
- sh:hasMeal (User -> Meal)
- sh:hasFoodItem (Meal -> FoodItem)
- sh:hasHabit (User -> Habit)
- sh:hasParticipation (User -> Participation)

**Query Examples:**
- "show users" → SELECT ?s ?name WHERE {{ ?s a sh:User . OPTIONAL {{ ?s sh:username ?name }} }}
- "show meals" → SELECT ?s WHERE {{ {{ ?s a sh:Breakfast }} UNION {{ ?s a sh:Lunch }} UNION {{ ?s a sh:Dinner }} UNION {{ ?s a sh:Snack }} }}
- "show activities" → SELECT ?s WHERE {{ {{ ?s a sh:Cardio }} UNION {{ ?s a sh:Musculation }} UNION {{ ?s a sh:Natation }} }}
- "show health metrics" → SELECT ?metric ?metricId ?metricName ?metricUnit WHERE {{ ?metric a sh:HealthMetric . ?metric sh:healthMetricId ?metricId . ?metric sh:healthMetricName ?metricName . OPTIONAL {{ ?metric sh:healthMetricUnit ?metricUnit }} }}

**INSERT Examples:**
- "add user John with email john@email.com" → 
  INSERT DATA {{ sh:User_John a sh:User ; sh:username "John" ; sh:email "john@email.com" }}
- "create activity Running" →
  INSERT DATA {{ sh:Activity_Running a sh:Cardio ; sh:activity_name "Running" }}
- "add meal Breakfast with 500 calories" →
  INSERT DATA {{ sh:Meal_1 a sh:Breakfast ; sh:total_calories 500 }}

**UPDATE Examples:**
- "update user John set email to newemail@test.com" →
  DELETE {{ ?u sh:email ?old }} INSERT {{ ?u sh:email "newemail@test.com" }} WHERE {{ ?u a sh:User ; sh:username "John" ; sh:email ?old }}
- "change activity Running duration to 45" →
  DELETE {{ ?a sh:duration ?old }} INSERT {{ ?a sh:duration 45 }} WHERE {{ ?a sh:activity_name "Running" ; sh:duration ?old }}

**DELETE Examples:**
- "delete user John" → DELETE WHERE {{ ?u a sh:User ; sh:username "John" . ?u ?p ?o }}
- "remove activity Running" → DELETE WHERE {{ ?a a sh:Cardio ; sh:activity_name "Running" . ?a ?p ?o }}
- "delete health metric poid" → DELETE WHERE {{ ?metric a sh:HealthMetric ; sh:healthMetricName "poid" . ?metric ?p ?o }}
- "remove health metric Cholesterol" → DELETE WHERE {{ ?metric a sh:HealthMetric ; sh:healthMetricName "Cholesterol" . ?metric ?p ?o }}

**CRITICAL RULES:**
1. Generate ONLY the SPARQL query, no explanations
2. Always include PREFIX definitions
3. Use the sh: namespace for all ontology terms
4. **FOR PARENT CLASSES WITH SUBCLASSES**:
   - **Meal, Activity, Habit**: DO NOT query the parent class directly, ALWAYS use UNION to query ALL subclasses
     Example: For "meals", query: {{ ?s a sh:Breakfast }} UNION {{ ?s a sh:Lunch }} UNION {{ ?s a sh:Dinner }} UNION {{ ?s a sh:Snack }}
   - **HealthMetric**: Query the parent class directly (sh:HealthMetric) because instances are stored as HealthMetric, not as subclasses
     Example: For "health metrics", query: ?metric a sh:HealthMetric
5. For user-specific queries, filter by user ID if provided
6. Return proper SELECT, INSERT DATA, DELETE/INSERT (UPDATE), or DELETE WHERE queries based on intent
7. For INSERT operations, generate unique IDs using underscore notation (e.g., sh:User_John)
8. For UPDATE operations, use DELETE/INSERT pattern
9. For DELETE operations, ensure all related triples are removed

**User Question:** {prompt}
"""
        
        if user_id:
            ontology_context += f"\n**User ID:** {user_id}"
        
        ontology_context += "\n\n**SPARQL Query:**"
        
        try:
            # Use REST API directly
            headers = {'Content-Type': 'application/json'}
            payload = {
                "contents": [{
                    "parts": [{"text": ontology_context}]
                }]
            }
            
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                return None, f"AI API Error: {response.status_code} - {response.text}"
            
            result = response.json()
            sparql_query = result['candidates'][0]['content']['parts'][0]['text'].strip()
            
            # Clean up the response - extract just the SPARQL query
            sparql_query = self._clean_sparql(sparql_query)
            
            return sparql_query, None
            
        except Exception as e:
            error_msg = f"AI Error: {str(e)}"
            if "API_KEY" in str(e).upper():
                error_msg = "Invalid or missing GEMINI_API_KEY. Get your free key at: https://makersuite.google.com/app/apikey"
            return None, error_msg
    
    def _clean_sparql(self, text):
        """Extract and clean SPARQL query from AI response"""
        # Remove markdown code blocks
        if "```sparql" in text:
            text = text.split("```sparql")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        # Remove any explanatory text before PREFIX
        if "PREFIX" in text:
            text = text[text.index("PREFIX"):]
        
        return text.strip()
    
    def analyze_intent(self, prompt):
        """Use AI to analyze the intent of the prompt"""
        if not self.enabled:
            return "query"
        
        intent_prompt = f"""
Analyze this prompt and return ONLY ONE WORD:
- "query" if it's asking for information
- "insert" if it's creating/adding new data
- "update" if it's modifying existing data
- "delete" if it's removing data

Prompt: {prompt}

Intent:"""
        
        try:
            payload = {
                "contents": [{
                    "parts": [{"text": intent_prompt}]
                }]
            }
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                json=payload
            )
            if response.status_code == 200:
                result = response.json()
                intent = result['candidates'][0]['content']['parts'][0]['text'].strip().lower()
                return intent if intent in ['query', 'insert', 'update', 'delete'] else 'query'
        except Exception:
            pass
        return 'query'
    
    def extract_entities(self, prompt):
        """Use AI to extract entities from prompt"""
        if not self.enabled:
            return {}
        
        entity_prompt = f"""
Extract entities from this prompt and return as JSON:
{{
  "user_id": null or number,
  "username": null or string,
  "email": null or string,
  "type": null or string (student/teacher/cardio/etc),
  "numbers": [] list of {{value: number, unit: string}}
}}

Prompt: {prompt}

JSON:"""
        
        try:
            payload = {
                "contents": [{
                    "parts": [{"text": entity_prompt}]
                }]
            }
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                json=payload
            )
            if response.status_code == 200:
                result = response.json()
                json_str = result['candidates'][0]['content']['parts'][0]['text'].strip()
                # Extract JSON from response
                if "{" in json_str:
                    json_str = json_str[json_str.index("{"):json_str.rindex("}")+1]
                return json.loads(json_str)
        except Exception:
            pass
        return {}
