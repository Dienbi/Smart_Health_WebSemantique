# Démarrage Rapide de Fuseki

## Problème : "Fuseki server is not running"

Si vous voyez cette erreur, Fuseki n'est pas démarré. Voici comment le démarrer rapidement.

## Solution Rapide (Docker - Recommandé)

### Étape 1 : Démarrer Docker Desktop

1. Ouvrir **Docker Desktop** (chercher dans le menu Démarrer)
2. Attendre que Docker soit complètement démarré (icône dans la barre des tâches)

### Étape 2 : Démarrer Fuseki

**Option A : Utiliser le script automatique**
```powershell
.\start_fuseki.bat
```

**Option B : Commande manuelle**
```powershell
docker-compose up -d fuseki
```

### Étape 3 : Vérifier que Fuseki fonctionne

Ouvrir dans le navigateur : http://localhost:3030

Vous devriez voir l'interface Fuseki.

### Étape 4 : Importer l'ontologie (première fois seulement)

```powershell
python scripts/import_ontology.py
```

### Étape 5 : Rafraîchir votre application web

Rechargez la page qui affichait l'erreur. Tout devrait fonctionner maintenant !

## Solution Alternative (Sans Docker)

Si vous avez Apache Jena Fuseki installé localement :

1. **Trouver Fuseki** :
   - Chercher `fuseki-server.bat` sur votre système
   - Ou télécharger depuis : https://jena.apache.org/download/

2. **Démarrer Fuseki** :
   ```powershell
   cd C:\apache-jena-fuseki-5.2.0  # ou le chemin où se trouve Fuseki
   .\fuseki-server.bat --update --mem /smarthealth
   ```

3. **Vérifier** : http://localhost:3030

4. **Importer l'ontologie** :
   - Aller sur : http://localhost:3030/dataset/smarthealth
   - Cliquer sur "upload"
   - Sélectionner : `ontology/smarthealth.ttl`

## Vérification Rapide

Pour vérifier si Fuseki est en cours d'exécution :

```powershell
# Vérifier avec Docker
docker-compose ps

# Ou tester directement
curl http://localhost:3030
```

## Commandes Utiles

### Arrêter Fuseki
```powershell
docker-compose stop fuseki
```

### Voir les logs
```powershell
docker-compose logs -f fuseki
```

### Redémarrer Fuseki
```powershell
docker-compose restart fuseki
```

## Dépannage

### Erreur : "Docker is not running"
→ Démarrer Docker Desktop avant de lancer Fuseki

### Erreur : "Port 3030 already in use"
→ Un autre service utilise déjà le port 3030
→ Arrêter l'autre service ou changer le port dans `docker-compose.yml`

### Erreur : "Cannot connect to Fuseki"
→ Vérifier que Fuseki est bien démarré : http://localhost:3030
→ Vérifier les logs : `docker-compose logs fuseki`

## Support

Si vous rencontrez toujours des problèmes :
1. Vérifier les logs : `docker-compose logs fuseki`
2. Vérifier que Docker Desktop est démarré
3. Vérifier que le port 3030 n'est pas utilisé par un autre service
4. Consulter `FUSEKI_SETUP.md` pour plus de détails

