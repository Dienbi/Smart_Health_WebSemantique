"""
RDF Manager for Smart Health - Meals and FoodItems
Gère les opérations CRUD en RDF/SPARQL pour les repas et les aliments
"""

from rdflib import Graph, Namespace, Literal, URIRef, RDF, RDFS, XSD
from pathlib import Path
import os
from datetime import datetime
from django.conf import settings


# Définir les namespaces
SMARTHEALTH = Namespace("http://dhia.org/ontologies/smarthealth#")

class RDFManager:
    """Gestionnaire RDF pour les opérations sur Meal et FoodItem"""
    
    def __init__(self):
        self.graph = Graph()
        self.graph.bind("smarthealth", SMARTHEALTH)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("xsd", XSD)
        
        # Chemin vers le fichier TTL
        self.ttl_path = os.path.join(settings.BASE_DIR, 'ontology', 'smarthealth.ttl')
        
        # Charger l'ontologie existante
        self.load_ontology()
    
    def load_ontology(self):
        """Charge l'ontologie depuis le fichier TTL"""
        try:
            if os.path.exists(self.ttl_path):
                self.graph.parse(self.ttl_path, format='turtle')
                print(f"[OK] Ontologie chargee : {len(self.graph)} triplets")
            else:
                print("[WARNING] Fichier ontologie non trouve, creation d'un nouveau graphe")
        except Exception as e:
            print(f"[ERROR] Erreur lors du chargement de l'ontologie : {e}")
    
    def save_ontology(self):
        """Sauvegarde l'ontologie dans le fichier TTL"""
        try:
            self.graph.serialize(destination=self.ttl_path, format='turtle')
            print(f"[SAVE] Ontologie sauvegardee : {len(self.graph)} triplets")
        except Exception as e:
            print(f"[ERROR] Erreur lors de la sauvegarde : {e}")
    
    # ==================== MEAL OPERATIONS ====================
    
    def create_meal(self, meal_id, meal_name, meal_type, total_calories, meal_date, user_id):
        """
        Crée un repas dans l'ontologie RDF
        
        Args:
            meal_id: ID du repas
            meal_name: Nom du repas
            meal_type: Type (BREAKFAST, LUNCH, DINNER, SNACK)
            total_calories: Calories totales
            meal_date: Date/heure du repas
            user_id: ID de l'utilisateur
        """
        # Créer l'URI du repas
        meal_uri = SMARTHEALTH[f"Meal_{meal_id}"]
        
        # Ajouter le type de classe selon meal_type
        type_mapping = {
            'BREAKFAST': SMARTHEALTH.Breakfast,
            'LUNCH': SMARTHEALTH.Lunch,
            'DINNER': SMARTHEALTH.Dinner,
            'SNACK': SMARTHEALTH.Snack
        }
        
        meal_class = type_mapping.get(meal_type, SMARTHEALTH.Meal)
        
        # Ajouter les triplets RDF
        self.graph.add((meal_uri, RDF.type, SMARTHEALTH.Meal))
        self.graph.add((meal_uri, RDF.type, meal_class))
        self.graph.add((meal_uri, SMARTHEALTH.mealId, Literal(meal_id, datatype=XSD.integer)))
        self.graph.add((meal_uri, SMARTHEALTH.name_meal, Literal(meal_name, datatype=XSD.string)))
        self.graph.add((meal_uri, SMARTHEALTH.calories_total, Literal(total_calories, datatype=XSD.integer)))
        
        # Ajouter la date si fournie
        if meal_date:
            # Convertir la date en format ISO
            if isinstance(meal_date, str):
                date_str = meal_date
            else:
                date_str = meal_date.isoformat()
            self.graph.add((meal_uri, SMARTHEALTH.meal_date, Literal(date_str, datatype=XSD.dateTime)))
        
        # Lier au user
        user_uri = SMARTHEALTH[f"User_{user_id}"]
        self.graph.add((user_uri, SMARTHEALTH.hasMeal, meal_uri))
        
        # Sauvegarder
        self.save_ontology()
        
        print(f"[OK] Meal cree en RDF : {meal_name} (ID: {meal_id})")
        return meal_uri
    
    def get_meal(self, meal_id):
        """Récupère un repas depuis l'ontologie"""
        meal_uri = SMARTHEALTH[f"Meal_{meal_id}"]
        
        # Requête SPARQL
        query = f"""
        PREFIX smarthealth: <http://dhia.org/ontologies/smarthealth#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        
        SELECT ?name ?calories ?date
        WHERE {{
            <{meal_uri}> smarthealth:name_meal ?name .
            <{meal_uri}> smarthealth:calories_total ?calories .
            OPTIONAL {{ <{meal_uri}> smarthealth:meal_date ?date }}
        }}
        """
        
        results = list(self.graph.query(query))
        
        if results:
            row = results[0]
            return {
                'meal_id': meal_id,
                'name': str(row.name),
                'calories': int(row.calories),
                'date': str(row.date) if row.date else None
            }
        return None
    
    def get_all_meals(self, user_id=None):
        """Récupère tous les repas (optionnellement filtrés par utilisateur)"""
        if user_id:
            query = f"""
            PREFIX smarthealth: <http://dhia.org/ontologies/smarthealth#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            
            SELECT ?meal ?mealId ?name ?calories ?date
            WHERE {{
                smarthealth:User_{user_id} smarthealth:hasMeal ?meal .
                ?meal smarthealth:mealId ?mealId .
                ?meal smarthealth:name_meal ?name .
                ?meal smarthealth:calories_total ?calories .
                OPTIONAL {{ ?meal smarthealth:meal_date ?date }}
            }}
            ORDER BY DESC(?date)
            """
        else:
            query = """
            PREFIX smarthealth: <http://dhia.org/ontologies/smarthealth#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            
            SELECT ?meal ?mealId ?name ?calories ?date
            WHERE {
                ?meal rdf:type smarthealth:Meal .
                ?meal smarthealth:mealId ?mealId .
                ?meal smarthealth:name_meal ?name .
                ?meal smarthealth:calories_total ?calories .
                OPTIONAL { ?meal smarthealth:meal_date ?date }
            }
            ORDER BY DESC(?date)
            """
        
        results = self.graph.query(query)
        meals = []
        
        for row in results:
            meals.append({
                'meal_id': int(row.mealId),
                'name': str(row.name),
                'calories': int(row.calories),
                'date': str(row.date) if row.date else None
            })
        
        return meals
    
    def update_meal(self, meal_id, meal_name=None, total_calories=None, meal_date=None):
        """Met à jour un repas dans l'ontologie"""
        meal_uri = SMARTHEALTH[f"Meal_{meal_id}"]
        
        # Supprimer les anciennes valeurs
        if meal_name is not None:
            self.graph.remove((meal_uri, SMARTHEALTH.name_meal, None))
            self.graph.add((meal_uri, SMARTHEALTH.name_meal, Literal(meal_name, datatype=XSD.string)))
        
        if total_calories is not None:
            self.graph.remove((meal_uri, SMARTHEALTH.calories_total, None))
            self.graph.add((meal_uri, SMARTHEALTH.calories_total, Literal(total_calories, datatype=XSD.integer)))
        
        if meal_date is not None:
            self.graph.remove((meal_uri, SMARTHEALTH.meal_date, None))
            if isinstance(meal_date, str):
                date_str = meal_date
            else:
                date_str = meal_date.isoformat()
            self.graph.add((meal_uri, SMARTHEALTH.meal_date, Literal(date_str, datatype=XSD.dateTime)))
        
        self.save_ontology()
        print(f"[OK] Meal mis a jour en RDF : ID {meal_id}")
    
    def delete_meal(self, meal_id):
        """Supprime un repas de l'ontologie"""
        meal_uri = SMARTHEALTH[f"Meal_{meal_id}"]
        
        # Supprimer tous les triplets liés au repas
        self.graph.remove((meal_uri, None, None))
        self.graph.remove((None, None, meal_uri))
        
        self.save_ontology()
        print(f"[OK] Meal supprime de RDF : ID {meal_id}")
    
    def link_fooditem_to_meal(self, meal_id, fooditem_id):
        """Lie un FoodItem à un Meal"""
        meal_uri = SMARTHEALTH[f"Meal_{meal_id}"]
        fooditem_uri = SMARTHEALTH[f"FoodItem_{fooditem_id}"]
        
        self.graph.add((meal_uri, SMARTHEALTH.hasFoodItem, fooditem_uri))
        self.save_ontology()
    
    def unlink_fooditem_from_meal(self, meal_id, fooditem_id):
        """Délie un FoodItem d'un Meal"""
        meal_uri = SMARTHEALTH[f"Meal_{meal_id}"]
        fooditem_uri = SMARTHEALTH[f"FoodItem_{fooditem_id}"]
        
        self.graph.remove((meal_uri, SMARTHEALTH.hasFoodItem, fooditem_uri))
        self.save_ontology()
    
    # ==================== FOODITEM OPERATIONS ====================
    
    def create_fooditem(self, fooditem_id, name, description, food_type, 
                       calories=None, protein=None, carbs=None, fiber=None, sugar=None):
        """
        Crée un FoodItem dans l'ontologie RDF
        
        Args:
            fooditem_id: ID de l'aliment
            name: Nom de l'aliment
            description: Description
            food_type: Type (PROTEIN, CARBS, FATS, VEGETABLES, FRUITS)
            calories, protein, carbs, fiber, sugar: Valeurs nutritionnelles optionnelles
        """
        fooditem_uri = SMARTHEALTH[f"FoodItem_{fooditem_id}"]
        
        # Ajouter les triplets de base
        self.graph.add((fooditem_uri, RDF.type, SMARTHEALTH.FoodItem))
        self.graph.add((fooditem_uri, SMARTHEALTH.foodItemId, Literal(fooditem_id, datatype=XSD.integer)))
        self.graph.add((fooditem_uri, SMARTHEALTH.foodItemName, Literal(name, datatype=XSD.string)))
        self.graph.add((fooditem_uri, SMARTHEALTH.foodItemDescription, Literal(description, datatype=XSD.string)))
        self.graph.add((fooditem_uri, SMARTHEALTH.type_FoodItem, Literal(food_type, datatype=XSD.string)))
        
        # Ajouter les informations nutritionnelles
        if calories is not None:
            calories_uri = SMARTHEALTH[f"Calories_{fooditem_id}"]
            self.graph.add((calories_uri, RDF.type, SMARTHEALTH.calories))
            self.graph.add((calories_uri, SMARTHEALTH.calories_value, Literal(calories, datatype=XSD.integer)))
            self.graph.add((fooditem_uri, SMARTHEALTH.hasCalories, calories_uri))
        
        if protein is not None:
            protein_uri = SMARTHEALTH[f"Protein_{fooditem_id}"]
            self.graph.add((protein_uri, RDF.type, SMARTHEALTH.protein))
            self.graph.add((protein_uri, SMARTHEALTH.protein_value, Literal(protein, datatype=XSD.integer)))
            self.graph.add((fooditem_uri, SMARTHEALTH.hasProtein, protein_uri))
        
        if carbs is not None:
            carbs_uri = SMARTHEALTH[f"Carbs_{fooditem_id}"]
            self.graph.add((carbs_uri, RDF.type, SMARTHEALTH.carbs))
            self.graph.add((carbs_uri, SMARTHEALTH.carbs_value, Literal(carbs, datatype=XSD.integer)))
            self.graph.add((fooditem_uri, SMARTHEALTH.hasCarbs, carbs_uri))
        
        if fiber is not None:
            fiber_uri = SMARTHEALTH[f"Fiber_{fooditem_id}"]
            self.graph.add((fiber_uri, RDF.type, SMARTHEALTH.fiber))
            self.graph.add((fiber_uri, SMARTHEALTH.fiber_value, Literal(fiber, datatype=XSD.integer)))
            self.graph.add((fooditem_uri, SMARTHEALTH.hasFiber, fiber_uri))
        
        if sugar is not None:
            sugar_uri = SMARTHEALTH[f"Sugar_{fooditem_id}"]
            self.graph.add((sugar_uri, RDF.type, SMARTHEALTH.sugar))
            self.graph.add((sugar_uri, SMARTHEALTH.sugar_value, Literal(sugar, datatype=XSD.integer)))
            self.graph.add((fooditem_uri, SMARTHEALTH.hasSugar, sugar_uri))
        
        self.save_ontology()
        print(f"[OK] FoodItem cree en RDF : {name} (ID: {fooditem_id})")
        return fooditem_uri
    
    def get_fooditem(self, fooditem_id):
        """Récupère un FoodItem depuis l'ontologie"""
        fooditem_uri = SMARTHEALTH[f"FoodItem_{fooditem_id}"]
        
        query = f"""
        PREFIX smarthealth: <http://dhia.org/ontologies/smarthealth#>
        
        SELECT ?name ?description ?type ?calories ?protein ?carbs ?fiber ?sugar
        WHERE {{
            <{fooditem_uri}> smarthealth:foodItemName ?name .
            <{fooditem_uri}> smarthealth:foodItemDescription ?description .
            <{fooditem_uri}> smarthealth:type_FoodItem ?type .
            OPTIONAL {{
                <{fooditem_uri}> smarthealth:hasCalories ?cal .
                ?cal smarthealth:calories_value ?calories .
            }}
            OPTIONAL {{
                <{fooditem_uri}> smarthealth:hasProtein ?prot .
                ?prot smarthealth:protein_value ?protein .
            }}
            OPTIONAL {{
                <{fooditem_uri}> smarthealth:hasCarbs ?carb .
                ?carb smarthealth:carbs_value ?carbs .
            }}
            OPTIONAL {{
                <{fooditem_uri}> smarthealth:hasFiber ?fib .
                ?fib smarthealth:fiber_value ?fiber .
            }}
            OPTIONAL {{
                <{fooditem_uri}> smarthealth:hasSugar ?sug .
                ?sug smarthealth:sugar_value ?sugar .
            }}
        }}
        """
        
        results = list(self.graph.query(query))
        
        if results:
            row = results[0]
            return {
                'fooditem_id': fooditem_id,
                'name': str(row.name),
                'description': str(row.description),
                'type': str(row.type),
                'calories': int(row.calories) if row.calories else None,
                'protein': int(row.protein) if row.protein else None,
                'carbs': int(row.carbs) if row.carbs else None,
                'fiber': int(row.fiber) if row.fiber else None,
                'sugar': int(row.sugar) if row.sugar else None
            }
        return None
    
    def get_all_fooditems(self):
        """Récupère tous les FoodItems"""
        query = """
        PREFIX smarthealth: <http://dhia.org/ontologies/smarthealth#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?fooditem ?fooditemId ?name ?description ?type
        WHERE {
            ?fooditem rdf:type smarthealth:FoodItem .
            ?fooditem smarthealth:foodItemId ?fooditemId .
            ?fooditem smarthealth:foodItemName ?name .
            ?fooditem smarthealth:foodItemDescription ?description .
            ?fooditem smarthealth:type_FoodItem ?type .
        }
        ORDER BY ?name
        """
        
        results = self.graph.query(query)
        fooditems = []
        
        for row in results:
            fooditems.append({
                'fooditem_id': int(row.fooditemId),
                'name': str(row.name),
                'description': str(row.description),
                'type': str(row.type)
            })
        
        return fooditems
    
    def update_fooditem(self, fooditem_id, name=None, description=None, food_type=None,
                       calories=None, protein=None, carbs=None, fiber=None, sugar=None):
        """Met à jour un FoodItem"""
        fooditem_uri = SMARTHEALTH[f"FoodItem_{fooditem_id}"]
        
        # Mettre à jour les propriétés de base
        if name is not None:
            self.graph.remove((fooditem_uri, SMARTHEALTH.foodItemName, None))
            self.graph.add((fooditem_uri, SMARTHEALTH.foodItemName, Literal(name, datatype=XSD.string)))
        
        if description is not None:
            self.graph.remove((fooditem_uri, SMARTHEALTH.foodItemDescription, None))
            self.graph.add((fooditem_uri, SMARTHEALTH.foodItemDescription, Literal(description, datatype=XSD.string)))
        
        if food_type is not None:
            self.graph.remove((fooditem_uri, SMARTHEALTH.type_FoodItem, None))
            self.graph.add((fooditem_uri, SMARTHEALTH.type_FoodItem, Literal(food_type, datatype=XSD.string)))
        
        # Mettre à jour les valeurs nutritionnelles
        if calories is not None:
            calories_uri = SMARTHEALTH[f"Calories_{fooditem_id}"]
            self.graph.remove((calories_uri, SMARTHEALTH.calories_value, None))
            self.graph.add((calories_uri, SMARTHEALTH.calories_value, Literal(calories, datatype=XSD.integer)))
        
        if protein is not None:
            protein_uri = SMARTHEALTH[f"Protein_{fooditem_id}"]
            self.graph.remove((protein_uri, SMARTHEALTH.protein_value, None))
            self.graph.add((protein_uri, SMARTHEALTH.protein_value, Literal(protein, datatype=XSD.integer)))
        
        if carbs is not None:
            carbs_uri = SMARTHEALTH[f"Carbs_{fooditem_id}"]
            self.graph.remove((carbs_uri, SMARTHEALTH.carbs_value, None))
            self.graph.add((carbs_uri, SMARTHEALTH.carbs_value, Literal(carbs, datatype=XSD.integer)))
        
        if fiber is not None:
            fiber_uri = SMARTHEALTH[f"Fiber_{fooditem_id}"]
            self.graph.remove((fiber_uri, SMARTHEALTH.fiber_value, None))
            self.graph.add((fiber_uri, SMARTHEALTH.fiber_value, Literal(fiber, datatype=XSD.integer)))
        
        if sugar is not None:
            sugar_uri = SMARTHEALTH[f"Sugar_{fooditem_id}"]
            self.graph.remove((sugar_uri, SMARTHEALTH.sugar_value, None))
            self.graph.add((sugar_uri, SMARTHEALTH.sugar_value, Literal(sugar, datatype=XSD.integer)))
        
        self.save_ontology()
        print(f"[OK] FoodItem mis a jour en RDF : ID {fooditem_id}")
    
    def delete_fooditem(self, fooditem_id):
        """Supprime un FoodItem"""
        fooditem_uri = SMARTHEALTH[f"FoodItem_{fooditem_id}"]
        
        # Supprimer aussi les valeurs nutritionnelles
        calories_uri = SMARTHEALTH[f"Calories_{fooditem_id}"]
        protein_uri = SMARTHEALTH[f"Protein_{fooditem_id}"]
        carbs_uri = SMARTHEALTH[f"Carbs_{fooditem_id}"]
        fiber_uri = SMARTHEALTH[f"Fiber_{fooditem_id}"]
        sugar_uri = SMARTHEALTH[f"Sugar_{fooditem_id}"]
        
        # Supprimer tous les triplets
        for uri in [fooditem_uri, calories_uri, protein_uri, carbs_uri, fiber_uri, sugar_uri]:
            self.graph.remove((uri, None, None))
            self.graph.remove((None, None, uri))
        
        self.save_ontology()
        print(f"[OK] FoodItem supprime de RDF : ID {fooditem_id}")
    
    # ==================== UTILITY METHODS ====================
    
    def get_next_meal_id(self):
        """Obtient le prochain ID disponible pour un Meal"""
        query = """
        PREFIX smarthealth: <http://dhia.org/ontologies/smarthealth#>
        
        SELECT (MAX(?id) AS ?maxId)
        WHERE {
            ?meal smarthealth:mealId ?id .
        }
        """
        results = list(self.graph.query(query))
        if results and results[0].maxId:
            return int(results[0].maxId) + 1
        return 1
    
    def get_next_fooditem_id(self):
        """Obtient le prochain ID disponible pour un FoodItem"""
        query = """
        PREFIX smarthealth: <http://dhia.org/ontologies/smarthealth#>
        
        SELECT (MAX(?id) AS ?maxId)
        WHERE {
            ?fooditem smarthealth:foodItemId ?id .
        }
        """
        results = list(self.graph.query(query))
        if results and results[0].maxId:
            return int(results[0].maxId) + 1
        return 1
    
    def execute_sparql(self, query):
        """Execute une requête SPARQL personnalisée"""
        return self.graph.query(query)
    
    def get_stats(self):
        """Retourne des statistiques sur l'ontologie"""
        return {
            'total_triples': len(self.graph),
            'total_meals': len(list(self.graph.subjects(RDF.type, SMARTHEALTH.Meal))),
            'total_fooditems': len(list(self.graph.subjects(RDF.type, SMARTHEALTH.FoodItem)))
        }


# Instance globale du gestionnaire RDF
rdf_manager = RDFManager()

