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
        # Use stable model names that are confirmed to work (as of Nov 2025)
        # Prioritize stable 2.5 versions which have better quota and performance
        models_to_try = [
            "gemini-2.5-flash",         # Best balance of speed and quota (stable)
            "gemini-flash-latest",      # Always points to latest flash
            "gemini-2.5-pro",           # More capable but slower (stable)
            "gemini-pro-latest",        # Always points to latest pro
        ]
        
        # Try to list available models first
        try:
            response = requests.get(
                f"{self.base_url}/models?key={self.api_key}",
                timeout=5
            )
            if response.status_code == 200:
                models_data = response.json().get('models', [])
                available_models = []
                for model in models_data:
                    if 'generateContent' in model.get('supportedGenerationMethods', []):
                        model_name = model['name'].replace('models/', '')
                        # Skip only experimental/preview models, keep stable 2.x versions
                        if '-exp' not in model_name and '-preview' not in model_name and 'thinking' not in model_name:
                            available_models.append(model_name)
                
                # Return first model from our priority list that's available
                for preferred in models_to_try:
                    if preferred in available_models:
                        return preferred
                
                # If none of our preferred models, use first available stable model
                if available_models:
                    return available_models[0]
        except Exception as e:
            print(f"Could not list models: {e}")
        
        # Fallback to most stable known model (as of Nov 2025)
        return "gemini-2.5-flash"
    
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
- sh:Habit (has subclasses: Reading, Cooking, Drawing, Journaling, Other - for habits like gym, exercise, meditation, etc.)
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
- "create activity running" →
  INSERT DATA {{ sh:Cardio_running a sh:Cardio ; sh:activity_name "running" }}
- "add activity weight lifting" →
  INSERT DATA {{ sh:Musculation_weightlifting a sh:Musculation ; sh:activity_name "weight lifting" }}
- "create activity swimming" →
  INSERT DATA {{ sh:Natation_swimming a sh:Natation ; sh:activity_name "swimming" }}
- "add breakfast meal pancakes with 400 calories" →
  INSERT DATA {{ sh:Breakfast_pancakes a sh:Breakfast ; sh:name "pancakes" ; sh:calories 400 }}
- "create dinner pasta 600 calories" →
  INSERT DATA {{ sh:Dinner_pasta a sh:Dinner ; sh:name "pasta" ; sh:calories 600 }}
- "add habit reading books" →
  INSERT DATA {{ sh:Reading_books a sh:Reading ; sh:habit_name "reading books" }}
- "create habit gym" →
  INSERT DATA {{ sh:Other_gym a sh:Other ; sh:habit_name "gym" }}
- "create health metric weight in kg" →
  INSERT DATA {{ sh:Weight_metric a sh:Weight ; sh:healthMetricName "weight" ; sh:healthMetricUnit "kg" }}
- "add challenge 30 day fitness" →
  INSERT DATA {{ sh:Defi_fitness a sh:Defi ; sh:defi_name "30 day fitness" ; sh:defi_description "Complete 30 days of exercise" }}

**UPDATE Examples:**
- "update user John set email to newemail@test.com" →
  DELETE {{ ?u sh:email ?old }} INSERT {{ ?u sh:email "newemail@test.com" }} WHERE {{ ?u a sh:User ; sh:username "John" ; sh:email ?old }}
- "change activity Running duration to 45" →
  DELETE {{ ?a sh:duration ?old }} INSERT {{ ?a sh:duration 45 }} WHERE {{ ?a sh:activity_name "Running" ; sh:duration ?old }}

**DELETE Examples:**
- "delete user John" → DELETE WHERE {{ ?u a sh:User ; sh:username "John" . ?u ?p ?o }}
- "remove activity Running" → DELETE WHERE {{ ?a sh:activity_name "Running" . ?a ?p ?o }}
- "delete habit test" → DELETE WHERE {{ ?h sh:habit_name "test" . ?h ?p ?o }}
- "delete habit gym" → DELETE WHERE {{ ?h sh:habit_name "gym" . ?h ?p ?o }}
- "delete health metric poid" → DELETE WHERE {{ ?metric sh:healthMetricName "poid" . ?metric ?p ?o }}
- "remove health metric Cholesterol" → DELETE WHERE {{ ?metric sh:healthMetricName "Cholesterol" . ?metric ?p ?o }}
- "delete meal pancakes" → DELETE WHERE {{ ?m sh:name "pancakes" . ?m ?p ?o }}

**CRITICAL RULES:**
1. Generate ONLY the SPARQL query, no explanations
2. Always include PREFIX definitions
3. Use the sh: namespace for all ontology terms
4. **FOR PARENT CLASSES WITH SUBCLASSES**:
   - **Meal, Activity, Habit**: For SELECT queries, use UNION to query ALL subclasses
     Example: For "show meals", query: {{ ?s a sh:Breakfast }} UNION {{ ?s a sh:Lunch }} UNION {{ ?s a sh:Dinner }} UNION {{ ?s a sh:Snack }}
   - **HealthMetric**: Query the parent class directly (sh:HealthMetric) because instances are stored as HealthMetric, not as subclasses
     Example: For "health metrics", query: ?metric a sh:HealthMetric
5. **FOR DELETE OPERATIONS**: DO NOT use UNION in DELETE WHERE. Match by unique property (name, ID, etc.) without specifying the class type
   - Example: DELETE WHERE {{ ?h sh:habit_name "test" . ?h ?p ?o }} (NOT: {{ ?h a sh:Other ; sh:habit_name "test" . ?h ?p ?o }})
   - Example: DELETE WHERE {{ ?m sh:name "pancakes" . ?m ?p ?o }} (for meals)
   - Example: DELETE WHERE {{ ?a sh:activity_name "Running" . ?a ?p ?o }} (for activities)
6. For user-specific queries, filter by user ID if provided
7. Return proper SELECT, INSERT DATA, DELETE/INSERT (UPDATE), or DELETE WHERE queries based on intent
8. For INSERT operations, generate unique IDs using underscore notation (e.g., sh:User_John)
9. For UPDATE operations, use DELETE/INSERT pattern
10. For DELETE operations, ensure all related triples are removed using ?p ?o pattern
11. **FOR MEAL INSERT**: ALWAYS include BOTH sh:name and sh:calories properties. Use format: sh:Breakfast_mealname a sh:Breakfast ; sh:name "mealname" ; sh:calories XXX
12. **FOR ACTIVITY INSERT**: ALWAYS include sh:activity_name property. Use format: sh:Cardio_activityname a sh:Cardio for cardio activities, sh:Musculation_activityname a sh:Musculation for strength training, sh:Natation_activityname a sh:Natation for swimming
13. **FOR HABIT INSERT**: ALWAYS include sh:habit_name property. For habits that don't fit Reading/Cooking/Drawing/Journaling, use sh:Other class (e.g., gym, meditation, exercise)
14. **ACTIVITY TYPE INFERENCE**: When creating activities, intelligently infer the type:
   - **Cardio (sh:Cardio)**: running, jogging, cycling, walking, sprinting, treadmill, elliptical, aerobics, dance, zumba, hiking, rope jumping
   - **Musculation (sh:Musculation)**: weight lifting, bench press, squats, deadlifts, push-ups, pull-ups, strength training, bodybuilding, resistance training, dumbbells, barbells
   - **Natation (sh:Natation)**: swimming, swim, freestyle, backstroke, breaststroke, butterfly, pool, laps
   - If unsure, default to **Cardio** for general movement activities

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
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                error_detail = response.text
                
                # Parse error for better user feedback
                if response.status_code == 429:
                    try:
                        error_json = response.json()
                        if 'error' in error_json and 'message' in error_json['error']:
                            message = error_json['error']['message']
                            if 'quota' in message.lower():
                                return None, "❌ API Quota Exceeded: You've hit the free tier limit (200 requests/day). Please wait or upgrade your plan at: https://ai.google.dev/pricing"
                    except:
                        pass
                    return None, "❌ API Rate Limit: Too many requests. Please wait a moment and try again."
                elif response.status_code == 404:
                    return None, f"❌ Model Not Found: The model '{self.model_name}' is not available. Trying to find alternative..."
                
                return None, f"AI API Error: {response.status_code} - {error_detail}"
            
            result = response.json()
            sparql_query = result['candidates'][0]['content']['parts'][0]['text'].strip()
            
            # Clean up the response - extract just the SPARQL query
            sparql_query = self._clean_sparql(sparql_query)
            
            return sparql_query, None
            
        except Exception as e:
            error_msg = f"AI Error: {str(e)}"
            if "API_KEY" in str(e).upper():
                error_msg = "Invalid or missing GEMINI_API_KEY. Get your free key at: https://makersuite.google.com/app/apikey"
            elif "timeout" in str(e).lower():
                error_msg = "AI service timeout. Please try again."
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
