# Implémentation CRUD avec RDF/SPARQL et Fuseki

## Vue d'ensemble

Le CRUD des `health_records` et `health_metrics` utilise maintenant **RDF/SPARQL avec Apache Fuseki** au lieu de Django ORM uniquement.

## Architecture

### Approche Hybride

1. **Django ORM** : Utilisé pour créer les objets et obtenir les IDs automatiques
2. **Fuseki (RDF/SPARQL)** : Utilisé pour stocker et interroger les données sémantiques
3. **Synchronisation automatique** : Les signaux Django synchronisent automatiquement les données entre Django et Fuseki

### Fichiers clés

#### 1. `apps/health_records/rdf_service.py`
Service principal pour convertir les modèles Django en triples RDF et exécuter les requêtes SPARQL.

**Méthodes principales :**
- `create_health_record_rdf(record)` : Convertit un HealthRecord en triples RDF
- `create_health_metric_rdf(metric)` : Convertit un HealthMetric en triples RDF
- `insert_health_record(record)` : Insère un HealthRecord dans Fuseki via SPARQL INSERT
- `insert_health_metric(metric)` : Insère un HealthMetric dans Fuseki via SPARQL INSERT
- `update_health_record(record)` : Met à jour un HealthRecord dans Fuseki via SPARQL DELETE/INSERT
- `delete_health_record(record_id)` : Supprime un HealthRecord de Fuseki via SPARQL DELETE
- `get_health_records_by_user(user_id)` : Récupère tous les health records d'un utilisateur via SPARQL SELECT
- `get_health_record_by_id(record_id)` : Récupère un health record spécifique via SPARQL SELECT
- `get_all_health_metrics()` : Récupère tous les health metrics via SPARQL SELECT

#### 2. `apps/health_records/signals.py`
Django signals pour synchronisation automatique :

- `post_save` sur `HealthRecord` : Insère/met à jour dans Fuseki automatiquement
- `post_delete` sur `HealthRecord` : Supprime de Fuseki automatiquement
- `post_save` sur `HealthMetric` : Insère/met à jour dans Fuseki automatiquement

#### 3. `apps/health_records/views.py`
Vues modifiées pour utiliser RDF/SPARQL :

- **`health_record_list_view`** : Lit depuis Fuseki (fallback sur Django ORM si échec)
- **`health_record_create_view`** : Crée dans Django, signal synchronise vers Fuseki
- **`health_record_update_view`** : Met à jour dans Django, signal synchronise vers Fuseki
- **`health_record_delete_view`** : Supprime dans Django, signal supprime de Fuseki
- **`health_record_detail_view`** : Lit depuis Fuseki (fallback sur Django ORM si échec)

## Format RDF

### URIs générées

- HealthRecord : `http://dhia.org/ontologies/smarthealth#HealthRecord_{id}`
- HealthMetric : `http://dhia.org/ontologies/smarthealth#HealthMetric_{id}`
- User : `http://dhia.org/ontologies/smarthealth#User_{id}`

### Propriétés RDF utilisées

#### HealthRecord
- `sh:healthRecordId` (xsd:int)
- `sh:healthRecordDescription` (xsd:string)
- `sh:healthRecordValue` (xsd:float)
- `sh:healthRecord_startDate` (xsd:dateTime)
- `sh:healthRecord_endDate` (xsd:dateTime)
- `sh:healthRecordCreatedAt` (xsd:dateTime)
- `sh:healthRecordDate` (xsd:dateTime) - pour compatibilité
- Relation : `sh:containsMetric` → HealthMetric
- Relation : `sh:hasHealthRecord` (depuis User)

#### HealthMetric
- `sh:healthMetricId` (xsd:int)
- `sh:healthMetricName` (xsd:string)
- `sh:healthMetricDescription` (xsd:string)
- `sh:healthMetricUnit` (xsd:string)
- `sh:healthMetricRecordedAt` (xsd:dateTime)

## Exemples de requêtes SPARQL

### INSERT (Création)

```sparql
PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

INSERT DATA {
    sh:HealthRecord_1 rdf:type sh:HealthRecord .
    sh:User_1 sh:hasHealthRecord sh:HealthRecord_1 .
    sh:HealthRecord_1 sh:healthRecordId 1 .
    sh:HealthRecord_1 sh:healthRecordDescription "Test record" .
    sh:HealthRecord_1 sh:healthRecordValue 75.5^^xsd:float .
    sh:HealthRecord_1 sh:healthRecord_startDate "2025-01-01T10:00:00Z"^^xsd:dateTime .
    sh:HealthRecord_1 sh:containsMetric sh:HealthMetric_1 .
}
```

### SELECT (Lecture)

```sparql
PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?recordId ?description ?value ?startDate ?metricName
WHERE {
    sh:User_1 sh:hasHealthRecord ?record .
    ?record sh:healthRecordId ?recordId .
    OPTIONAL { ?record sh:healthRecordDescription ?description . }
    OPTIONAL { ?record sh:healthRecordValue ?value . }
    OPTIONAL { ?record sh:healthRecord_startDate ?startDate . }
    OPTIONAL {
        ?record sh:containsMetric ?metric .
        ?metric sh:healthMetricName ?metricName .
    }
}
```

### UPDATE (Modification)

```sparql
PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

DELETE {
    sh:HealthRecord_1 ?p ?o .
    ?user sh:hasHealthRecord sh:HealthRecord_1 .
}
INSERT {
    sh:HealthRecord_1 rdf:type sh:HealthRecord .
    sh:User_1 sh:hasHealthRecord sh:HealthRecord_1 .
    sh:HealthRecord_1 sh:healthRecordDescription "Updated description" .
}
WHERE {
    OPTIONAL { sh:HealthRecord_1 ?p ?o . }
    OPTIONAL { ?user sh:hasHealthRecord sh:HealthRecord_1 . }
}
```

### DELETE (Suppression)

```sparql
PREFIX sh: <http://dhia.org/ontologies/smarthealth#>

DELETE WHERE {
    sh:HealthRecord_1 ?p ?o .
    ?user sh:hasHealthRecord sh:HealthRecord_1 .
}
```

## Avantages de cette approche

1. **Stockage sémantique** : Les données sont stockées dans un format RDF, permettant des requêtes sémantiques complexes
2. **Interopérabilité** : Les données peuvent être partagées avec d'autres systèmes utilisant RDF/SPARQL
3. **Requêtes avancées** : SPARQL permet des requêtes complexes que SQL ne peut pas facilement gérer
4. **Compatibilité** : Fallback sur Django ORM si Fuseki n'est pas disponible
5. **Synchronisation automatique** : Les signaux Django garantissent la cohérence entre Django et Fuseki

## Configuration requise

### Variables d'environnement

```env
FUSEKI_ENDPOINT=http://localhost:3030/smarthealth/sparql
FUSEKI_UPDATE_ENDPOINT=http://localhost:3030/smarthealth/update
```

### Démarrage de Fuseki

```powershell
# Windows
cd C:\apache-jena-fuseki-5.2.0
.\fuseki-server.bat --update --mem /smarthealth

# Ou via Docker
docker-compose up fuseki
```

## Utilisation

### Créer un HealthRecord

1. L'utilisateur remplit le formulaire sur `/health/`
2. Django crée l'objet dans SQLite (obtient l'ID)
3. Le signal `post_save` détecte la création
4. Le signal appelle `rdf_service.insert_health_record()`
5. Les triples RDF sont insérés dans Fuseki via SPARQL INSERT

### Lire les HealthRecords

1. L'utilisateur visite `/health/`
2. La vue appelle `rdf_service.get_health_records_by_user()`
3. Une requête SPARQL SELECT est exécutée sur Fuseki
4. Les résultats sont convertis en objets Django-like pour le template
5. Si Fuseki échoue, fallback sur Django ORM

### Modifier un HealthRecord

1. L'utilisateur modifie via le formulaire
2. Django met à jour l'objet dans SQLite
3. Le signal `post_save` détecte la modification
4. Le signal appelle `rdf_service.update_health_record()`
5. Les anciens triples sont supprimés et les nouveaux sont insérés dans Fuseki

### Supprimer un HealthRecord

1. L'utilisateur clique sur "Delete"
2. Django supprime l'objet de SQLite
3. Le signal `post_delete` détecte la suppression
4. Le signal appelle `rdf_service.delete_health_record()`
5. Les triples sont supprimés de Fuseki via SPARQL DELETE

## Dépannage

### Fuseki non accessible

Si Fuseki n'est pas accessible, le système bascule automatiquement sur Django ORM. Vérifiez :
- Fuseki est démarré
- Les endpoints sont corrects dans `.env`
- Le dataset `smarthealth` existe

### Données non synchronisées

Si les données ne sont pas synchronisées :
1. Vérifiez les logs Django pour les erreurs SPARQL
2. Vérifiez que les signals sont bien enregistrés (`apps.py`)
3. Redémarrez le serveur Django après modification des signals

### Requêtes SPARQL échouent

Vérifiez :
- La syntaxe SPARQL dans `rdf_service.py`
- Les URIs générées sont correctes
- Les propriétés existent dans l'ontologie `smarthealth.ttl`

