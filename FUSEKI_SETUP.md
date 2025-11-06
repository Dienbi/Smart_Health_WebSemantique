# Guide de démarrage de Fuseki

## Problème : "Fuseki server is not running"

Si vous voyez l'erreur `ConnectionRefusedError` ou `Fuseki server is not running`, cela signifie que le serveur Fuseki n'est pas démarré.

## Solutions

### Option 1 : Démarrer Fuseki manuellement (Windows)

1. **Télécharger Apache Jena Fuseki** (si pas déjà fait) :
   - Télécharger depuis : https://jena.apache.org/download/
   - Extraire dans un dossier (ex: `C:\apache-jena-fuseki-5.2.0`)

2. **Démarrer Fuseki** :
   ```powershell
   cd C:\apache-jena-fuseki-5.2.0
   .\fuseki-server.bat --update --mem /smarthealth
   ```

3. **Vérifier** :
   - Ouvrir : http://localhost:3030
   - Vous devriez voir l'interface Fuseki

### Option 2 : Utiliser Docker

1. **Démarrer Fuseki via Docker Compose** :
   ```powershell
   docker-compose up fuseki
   ```

2. **Vérifier** :
   - Ouvrir : http://localhost:3030
   - Le dataset `smarthealth` devrait être disponible

### Option 3 : Démarrer Fuseki en arrière-plan (Windows Service)

Pour démarrer Fuseki automatiquement en arrière-plan :

1. **Créer un fichier batch** `start_fuseki.bat` :
   ```batch
   @echo off
   cd C:\apache-jena-fuseki-5.2.0
   start /B fuseki-server.bat --update --mem /smarthealth
   ```

2. **Ou utiliser NSSM** (Non-Sucking Service Manager) pour créer un service Windows :
   ```powershell
   # Télécharger NSSM depuis https://nssm.cc/download
   # Installer Fuseki comme service
   nssm install Fuseki "C:\apache-jena-fuseki-5.2.0\fuseki-server.bat" "--update --mem /smarthealth"
   nssm start Fuseki
   ```

## Configuration

### Vérifier les endpoints

Dans votre fichier `.env`, vous devriez avoir :

```env
FUSEKI_ENDPOINT=http://localhost:3030/smarthealth/sparql
FUSEKI_UPDATE_ENDPOINT=http://localhost:3030/smarthealth/update
```

### Créer le dataset `smarthealth`

Si le dataset n'existe pas :

1. Aller sur : http://localhost:3030
2. Cliquer sur "Add dataset"
3. Nom : `smarthealth`
4. Type : `in-memory` ou `persistent`
5. Cliquer sur "Create dataset"

### Importer l'ontologie

Après avoir créé le dataset, importer l'ontologie :

1. Aller sur : http://localhost:3030/dataset/smarthealth
2. Cliquer sur "upload"
3. Sélectionner le fichier : `ontology/smarthealth.ttl`
4. Cliquer sur "Upload"

Ou utiliser le script Python :

```powershell
python scripts/import_ontology.py
```

## Vérification

### Test de connexion

```powershell
python scripts/test_fuseki.py
```

Ou tester manuellement :

```powershell
# Test simple
curl http://localhost:3030/smarthealth/sparql?query=SELECT%20*%20WHERE%20%7B%20?s%20?p%20?o%20%7D%20LIMIT%201
```

## Dépannage

### Port 3030 déjà utilisé

Si le port 3030 est déjà utilisé :

1. **Changer le port** :
   ```powershell
   .\fuseki-server.bat --port=3031 --update --mem /smarthealth
   ```

2. **Mettre à jour `.env`** :
   ```env
   FUSEKI_ENDPOINT=http://localhost:3031/smarthealth/sparql
   FUSEKI_UPDATE_ENDPOINT=http://localhost:3031/smarthealth/update
   ```

### Fuseki ne démarre pas

1. **Vérifier Java** :
   ```powershell
   java -version
   ```
   Fuseki nécessite Java 11 ou supérieur.

2. **Vérifier les logs** :
   - Regarder la console pour les erreurs
   - Vérifier les logs dans `C:\apache-jena-fuseki-5.2.0\run\`

### Données perdues après redémarrage

Si vous utilisez `--mem` (in-memory), les données sont perdues après redémarrage.

**Solution** : Utiliser un dataset persistant :

```powershell
.\fuseki-server.bat --update --tdb2 --loc=./databases/smarthealth /smarthealth
```

## Notes importantes

- **Fuseki doit être démarré avant Django** pour que les requêtes SPARQL fonctionnent
- **Les données en mémoire (`--mem`) sont perdues** à chaque redémarrage
- **Pour la production**, utilisez un dataset persistant avec `--tdb2`
- **Vérifiez toujours** que Fuseki est accessible avant d'utiliser les fonctionnalités RDF/SPARQL

