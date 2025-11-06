# 🍳 FoodItem CRUD - Guide de démarrage rapide

## 🎯 Objectif

Ce système CRUD permet aux administrateurs de gérer complètement les **aliments (FoodItems)** dans le dashboard admin de Smart Health, avec toutes les informations nutritionnelles associées.

## 🚀 Installation et Configuration

### 1. Vérifier les dépendances

Assurez-vous que tous les packages sont installés :

```bash
pip install -r requirements.txt
```

### 2. Créer les données de test

Exécutez le script de test pour créer des données d'exemple :

```bash
python scripts/test_fooditem_crud.py
```

Ce script va créer :
- ✅ 1 utilisateur admin (admin / admin123)
- ✅ 1 utilisateur test (testuser / test123)
- ✅ 4 repas différents (Breakfast, Lunch, Dinner, Snack)
- ✅ 12 aliments avec informations nutritionnelles complètes

### 3. Appliquer les migrations (si nécessaire)

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Démarrer le serveur

```bash
python manage.py runserver
```

## 📍 Accès à l'interface

### URL principale du backoffice FoodItem
```
http://127.0.0.1:8000/backoffice/fooditems/
```

### Authentification
1. Connectez-vous d'abord au système : http://127.0.0.1:8000/login/
2. Utilisez les identifiants : **admin / admin123**
3. Accédez au dashboard : http://127.0.0.1:8000/dashboard/
4. Dans le menu sidebar, cliquez sur **FoodItems**

## 🎨 Fonctionnalités disponibles

### 📋 1. Liste des aliments
**URL:** `/backoffice/fooditems/`

**Fonctionnalités:**
- ✅ Affichage paginé (20 aliments par page)
- ✅ Recherche par nom d'aliment
- ✅ Filtrage par type (Protéines, Glucides, Lipides, Légumes, Fruits)
- ✅ Affichage des valeurs nutritionnelles principales
- ✅ Actions rapides : Voir, Modifier, Supprimer

**Exemple de recherche:**
```
http://127.0.0.1:8000/backoffice/fooditems/?search=poulet
http://127.0.0.1:8000/backoffice/fooditems/?type=PROTEIN
```

### ➕ 2. Créer un aliment
**URL:** `/backoffice/fooditems/create/`

**Champs obligatoires:**
- 🍽️ Repas associé
- 📝 Nom de l'aliment
- 📄 Description
- 🏷️ Type d'aliment

**Champs optionnels (Nutrition):**
- 🔥 Calories (cal)
- 🥚 Protéines (g)
- 🍞 Glucides (g)
- 🌾 Fibres (g)
- 🍯 Sucres (g)

### 👁️ 3. Voir les détails
**URL:** `/backoffice/fooditems/<id>/`

**Affichage:**
- Informations de base complètes
- Toutes les valeurs nutritionnelles
- Informations sur le repas associé
- Actions : Modifier, Supprimer

### ✏️ 4. Modifier un aliment
**URL:** `/backoffice/fooditems/<id>/edit/`

**Fonctionnalités:**
- Formulaire pré-rempli avec les données existantes
- Modification de tous les champs
- Mise à jour des valeurs nutritionnelles

### 🗑️ 5. Supprimer un aliment
**URL:** `/backoffice/fooditems/<id>/delete/`

**Attention:**
- ⚠️ Suppression définitive
- ⚠️ Supprime aussi toutes les données nutritionnelles associées
- ✅ Page de confirmation avec détails

## 🎨 Types d'aliments et couleurs

Le système utilise 5 types d'aliments avec des badges colorés :

| Type | Code | Couleur | Icône |
|------|------|---------|-------|
| Protéines | `PROTEIN` | 🔵 Bleu | 🥚 |
| Glucides | `CARBS` | 🟠 Orange | 🍞 |
| Lipides | `FATS` | 🔴 Rose | 🥑 |
| Légumes | `VEGETABLES` | 🟢 Vert | 🥦 |
| Fruits | `FRUITS` | 🟣 Violet | 🍎 |

## 📊 Structure de la base de données

```
FoodItem (Aliment principal)
├── meal_id (FK) → Meal
├── food_item_name (VARCHAR)
├── food_item_description (TEXT)
├── food_type (CHOICE)
│
├── Calories (OneToOne)
│   └── calories_value (INT)
│
├── Protein (OneToOne)
│   └── protein_value (INT)
│
├── Carbs (OneToOne)
│   └── carbs_value (INT)
│
├── Fiber (OneToOne)
│   └── fiber_value (INT)
│
└── Sugar (OneToOne)
    └── sugar_value (INT)
```

## 🔐 Permissions

**Accès requis:**
- ✅ Utilisateur connecté (`@login_required`)
- ✅ Statut staff (`is_staff=True`)

**Comment donner les permissions:**

```python
# Via Python shell
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(username='username')
user.is_staff = True
user.save()
```

Ou via l'admin Django natif : http://127.0.0.1:8000/admin/

## 🧪 Tests

### Test manuel complet

1. **Liste** : Vérifier l'affichage des aliments
2. **Recherche** : Tester la recherche par nom
3. **Filtres** : Filtrer par type d'aliment
4. **Création** : Créer un nouvel aliment avec nutrition
5. **Détails** : Visualiser les détails complets
6. **Modification** : Modifier un aliment existant
7. **Suppression** : Supprimer un aliment (tester la confirmation)
8. **Pagination** : Naviguer entre les pages

### Exemples de données à tester

**Aliment protéiné:**
```
Nom: Thon en conserve
Description: Thon naturel égoutté
Type: PROTEIN
Calories: 120 cal
Protéines: 26 g
Glucides: 0 g
Fibres: 0 g
Sucres: 0 g
```

**Aliment glucidique:**
```
Nom: Pâtes complètes
Description: Pâtes de blé complet cuites
Type: CARBS
Calories: 180 cal
Protéines: 7 g
Glucides: 38 g
Fibres: 6 g
Sucres: 2 g
```

## 🐛 Résolution de problèmes

### Problème : "Permission denied"
**Solution:**
```bash
# Vérifier le statut staff de l'utilisateur
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(username='admin')
>>> print(f"is_staff: {user.is_staff}")
>>> user.is_staff = True
>>> user.save()
```

### Problème : "Page not found (404)"
**Solution:** Vérifier que les URLs sont bien configurées dans `Smart_Health/urls.py`

### Problème : Styles non appliqués
**Solution:** 
1. Vérifier que `admin_base.html` charge Bootstrap
2. Vider le cache du navigateur (Ctrl+Shift+R)
3. Vérifier la console du navigateur pour les erreurs

### Problème : Formulaire ne soumet pas
**Solution:** Vérifier que le token CSRF est présent : `{% csrf_token %}`

## 📚 Documentation complète

Pour plus de détails, consultez :
- 📖 **FOODITEM_CRUD_DOCUMENTATION.md** : Documentation technique complète
- 🎓 **API_DOCUMENTATION.md** : Documentation de l'API REST

## 🎯 Exemples d'utilisation

### Créer un aliment via le backoffice

1. Accédez à http://127.0.0.1:8000/backoffice/fooditems/
2. Cliquez sur "Ajouter un Aliment"
3. Remplissez le formulaire :
   - **Repas** : Sélectionnez "Déjeuner équilibré"
   - **Nom** : "Steak de bœuf"
   - **Description** : "Steak de bœuf grillé 150g"
   - **Type** : "Protéines"
   - **Calories** : 280
   - **Protéines** : 42
   - **Glucides** : 0
   - **Fibres** : 0
   - **Sucres** : 0
4. Cliquez sur "Créer"

### Rechercher des aliments

```
# Rechercher tous les aliments contenant "poulet"
http://127.0.0.1:8000/backoffice/fooditems/?search=poulet

# Afficher seulement les fruits
http://127.0.0.1:8000/backoffice/fooditems/?type=FRUITS

# Combiner recherche et filtre
http://127.0.0.1:8000/backoffice/fooditems/?search=pomme&type=FRUITS
```

## 🎨 Personnalisation

### Changer les couleurs des types
Modifiez dans `templates/admin/meals/fooditem_list.html` :

```css
.type-protein { background: #e3f2fd; color: #1976d2; }
.type-carbs { background: #fff3e0; color: #f57c00; }
.type-fats { background: #fce4ec; color: #c2185b; }
.type-vegetables { background: #e8f5e9; color: #388e3c; }
.type-fruits { background: #f3e5f5; color: #7b1fa2; }
```

### Ajouter un nouveau type d'aliment

1. Modifiez `apps/meals/models.py` :
```python
FOOD_TYPE_CHOICES = [
    ('PROTEIN', 'Protein'),
    ('CARBS', 'Carbohydrates'),
    ('FATS', 'Fats'),
    ('VEGETABLES', 'Vegetables'),
    ('FRUITS', 'Fruits'),
    ('DAIRY', 'Dairy'),  # Nouveau type
]
```

2. Créez une migration :
```bash
python manage.py makemigrations
python manage.py migrate
```

## 🤝 Contribution

Pour améliorer ce système :
1. Fork le projet
2. Créez une branche (`git checkout -b feature/amelioration`)
3. Committez vos changements
4. Pushez vers la branche
5. Ouvrez une Pull Request

## 📞 Support

Pour toute question ou problème :
- 📧 Email : support@smarthealth.com
- 💬 Issues GitHub : [Créer une issue]
- 📖 Documentation : FOODITEM_CRUD_DOCUMENTATION.md

---

**Développé avec ❤️ pour Smart Health**  
Version 1.0 - Novembre 2025


