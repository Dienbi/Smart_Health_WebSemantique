# Documentation CRUD FoodItem - Dashboard Admin

## 📋 Vue d'ensemble

Ce document décrit le système CRUD complet pour la gestion des **FoodItems** (Aliments) dans le dashboard administrateur de Smart Health. Ce système permet aux administrateurs de créer, lire, mettre à jour et supprimer des aliments avec leurs informations nutritionnelles complètes.

## 🎯 Fonctionnalités

### 1. **Liste des Aliments** (`/backoffice/fooditems/`)
- Affichage paginé de tous les aliments (20 par page)
- Recherche par nom d'aliment
- Filtrage par type d'aliment (Protéines, Glucides, Lipides, Légumes, Fruits)
- Affichage des informations nutritionnelles principales
- Actions rapides : Voir, Modifier, Supprimer

**Colonnes affichées :**
- ID de l'aliment
- Nom
- Description (tronquée)
- Type (avec badge coloré)
- Informations nutritionnelles (calories, protéines, glucides)
- Repas associé
- Actions

### 2. **Créer un Aliment** (`/backoffice/fooditems/create/`)
- Formulaire complet pour ajouter un nouvel aliment
- Champs obligatoires : Repas, Nom, Description, Type
- Informations nutritionnelles optionnelles mais recommandées :
  - Calories (cal)
  - Protéines (g)
  - Glucides (g)
  - Fibres (g)
  - Sucres (g)
- Design moderne avec icônes Bootstrap
- Validation des données côté serveur

### 3. **Voir les Détails** (`/backoffice/fooditems/<id>/`)
- Affichage complet de toutes les informations
- En-tête avec gradient et informations principales
- Section informations de base
- Section nutritionnelle avec cartes visuelles
- Actions : Retour, Modifier, Supprimer

### 4. **Modifier un Aliment** (`/backoffice/fooditems/<id>/edit/`)
- Formulaire pré-rempli avec les données existantes
- Modification de toutes les informations
- Mise à jour des valeurs nutritionnelles
- Validation et sauvegarde

### 5. **Supprimer un Aliment** (`/backoffice/fooditems/<id>/delete/`)
- Page de confirmation avec avertissement
- Affichage des détails de l'aliment à supprimer
- Information sur la suppression en cascade des données nutritionnelles
- Confirmation requise avant suppression

## 🎨 Design et UX

Le design suit le template du dashboard admin avec :
- **Couleurs cohérentes** : Bleu primaire (#1e88e5) et bleu secondaire (#0d47a1)
- **Badges colorés** pour les types d'aliments :
  - 🔵 Protéines : Bleu clair
  - 🟠 Glucides : Orange
  - 🔴 Lipides : Rose
  - 🟢 Légumes : Vert
  - 🟣 Fruits : Violet
- **Icônes Bootstrap** pour une meilleure visualisation
- **Animations** : Transitions fluides sur les boutons et cartes
- **Responsive** : Design adapté aux différentes tailles d'écran

## 📁 Structure des fichiers

```
Smart_Health/
├── apps/meals/
│   ├── views.py                    # Vues CRUD pour FoodItem
│   ├── back_urls.py                # URLs du backoffice
│   ├── models.py                   # Modèles (FoodItem, Calories, etc.)
│   └── admin.py                    # Admin Django natif
├── templates/admin/meals/
│   ├── fooditem_list.html          # Liste des aliments
│   ├── fooditem_form.html          # Formulaire création/modification
│   ├── fooditem_detail.html        # Détails d'un aliment
│   └── fooditem_confirm_delete.html # Confirmation de suppression
└── Smart_Health/
    └── urls.py                     # Configuration URLs principale
```

## 🔗 URLs et Navigation

### URLs du Backoffice
```python
/backoffice/fooditems/              # Liste
/backoffice/fooditems/create/       # Créer
/backoffice/fooditems/<id>/         # Détails
/backoffice/fooditems/<id>/edit/    # Modifier
/backoffice/fooditems/<id>/delete/  # Supprimer
```

### Navigation dans le menu
Le menu sidebar du dashboard admin contient maintenant :
```
📊 Dashboard
🚩 Défis
   └─ Gérer Défis
   └─ Créer Défi
🍳 FoodItems
   └─ Gérer Aliments
   └─ Ajouter Aliment
🚪 Logout
```

## 🔐 Sécurité et Permissions

- **Authentification requise** : Toutes les vues nécessitent une connexion
- **Permission Staff** : Seuls les utilisateurs avec `is_staff=True` peuvent accéder
- **Mixin `StaffRequiredMixin`** : Vérifie automatiquement les permissions
- **Protection CSRF** : Tous les formulaires incluent le token CSRF

## 💾 Gestion des données

### Modèles liés
```
FoodItem (parent)
├── Meal (ForeignKey)
├── Calories (OneToOne)
├── Protein (OneToOne)
├── Carbs (OneToOne)
├── Fiber (OneToOne)
└── Sugar (OneToOne)
```

### Suppression en cascade
Lorsqu'un FoodItem est supprimé, toutes les informations nutritionnelles associées sont automatiquement supprimées grâce aux relations `OneToOne` avec `on_delete=models.CASCADE`.

## 🚀 Utilisation

### Pour créer un nouvel aliment :
1. Connectez-vous en tant qu'admin
2. Accédez au dashboard admin
3. Cliquez sur "FoodItems" > "Ajouter Aliment"
4. Remplissez le formulaire :
   - Sélectionnez le repas
   - Entrez le nom de l'aliment
   - Ajoutez une description
   - Choisissez le type
   - Ajoutez les valeurs nutritionnelles (optionnel)
5. Cliquez sur "Créer"

### Pour modifier un aliment :
1. Accédez à "FoodItems" > "Gérer Aliments"
2. Trouvez l'aliment dans la liste (utilisez la recherche/filtres)
3. Cliquez sur l'icône crayon (Modifier)
4. Modifiez les champs souhaités
5. Cliquez sur "Mettre à jour"

### Pour supprimer un aliment :
1. Accédez à "FoodItems" > "Gérer Aliments"
2. Cliquez sur l'icône poubelle (Supprimer)
3. Vérifiez les détails sur la page de confirmation
4. Cliquez sur "Supprimer définitivement"

## 📊 Fonctionnalités avancées

### Recherche et filtrage
```python
# Recherche par nom
?search=poulet

# Filtrage par type
?type=PROTEIN

# Combinaison
?search=poulet&type=PROTEIN
```

### Pagination
- 20 éléments par page
- Navigation : Première, Précédente, Suivante, Dernière
- Affichage du numéro de page actuel

### Optimisation des requêtes
Les vues utilisent `select_related()` et `prefetch_related()` pour optimiser les requêtes à la base de données :
```python
queryset = FoodItem.objects.select_related('meal', 'meal__user').prefetch_related(
    'calories', 'protein', 'carbs', 'fiber', 'sugar'
)
```

## 🎓 Classes et méthodes principales

### Vues (views.py)
- `AdminFoodItemListView` : Liste avec recherche/filtres
- `AdminFoodItemDetailView` : Affichage détaillé
- `AdminFoodItemCreateView` : Création avec nutrition
- `AdminFoodItemUpdateView` : Modification complète
- `AdminFoodItemDeleteView` : Suppression avec confirmation

### Mixin
- `StaffRequiredMixin` : Contrôle d'accès staff uniquement

## 🔧 Configuration requise

### Dépendances
- Django 4.2+
- Bootstrap 5.3
- Bootstrap Icons 1.11

### Templates requis
- `admin_base.html` : Template de base du dashboard admin

## 📝 Notes importantes

1. **Repas obligatoire** : Un aliment doit toujours être associé à un repas
2. **Valeurs nutritionnelles optionnelles** : Peuvent être ajoutées/modifiées à tout moment
3. **Types d'aliments** : 5 catégories prédéfinies (PROTEIN, CARBS, FATS, VEGETABLES, FRUITS)
4. **Validation** : Les valeurs nutritionnelles doivent être des entiers positifs
5. **Cascade** : La suppression d'un repas supprime automatiquement ses aliments

## 🐛 Troubleshooting

### Problème : Page 404 en accédant au backoffice
**Solution** : Vérifiez que les URLs sont bien configurées dans `Smart_Health/urls.py`

### Problème : Erreur de permission
**Solution** : Assurez-vous que l'utilisateur a `is_staff=True`

### Problème : Styles non appliqués
**Solution** : Vérifiez que Bootstrap est bien chargé dans `admin_base.html`

## 🎉 Prochaines améliorations possibles

- [ ] Import/Export CSV des aliments
- [ ] Gestion des images d'aliments
- [ ] Catégories personnalisées
- [ ] Suggestions d'aliments similaires
- [ ] Statistiques d'utilisation
- [ ] API REST pour mobile
- [ ] Duplication d'aliments
- [ ] Historique des modifications

---

**Développé pour Smart Health WebSémantique**  
**Date de création** : Novembre 2025  
**Version** : 1.0

