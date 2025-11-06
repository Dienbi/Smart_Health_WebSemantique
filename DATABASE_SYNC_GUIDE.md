# Database Synchronization System

## Overview

This application uses **two databases** that are kept synchronized:

1. **Django SQLite Database** - Used by CRUD interfaces
2. **Apache Fuseki (RDF/SPARQL)** - Used by AI queries

## Synchronization Architecture

```
┌─────────────────────────────────────────────────┐
│           Smart Health Application              │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────┐          ┌──────────────┐    │
│  │   Django     │          │   AI Service │    │
│  │   CRUD       │◄────────►│   (Gemini)   │    │
│  │   Forms      │   Sync   │              │    │
│  └──────┬───────┘          └──────┬───────┘    │
│         │                         │            │
│         ▼                         ▼            │
│  ┌──────────────┐          ┌──────────────┐    │
│  │  SQLite DB   │          │ Fuseki RDF   │    │
│  │  (Django)    │◄────────►│  (SPARQL)    │    │
│  └──────────────┘   Sync   └──────────────┘    │
│         ✅ BI-DIRECTIONAL SYNC ✅               │
└─────────────────────────────────────────────────┘
```

## How It Works

### Direction 1: Django → Fuseki (Django Signals)

When you create/update/delete data using **CRUD forms**:

1. **Django saves to SQLite** first
2. **Django Signal is triggered** automatically
3. **Signal handler syncs to Fuseki** using SPARQL INSERT/UPDATE/DELETE

**Implemented for:**

- ✅ Health Records (HealthRecord, HealthMetric)
- ✅ Meals (Meal, FoodItem)
- ✅ Activities (Activity, ActivityLog)
- ✅ Habits (Habit, HabitLog)

**Files:**

- `apps/health_records/signals.py`
- `apps/meals/signals.py`
- `apps/activities/signals.py`
- `apps/habits/signals.py`

### Direction 2: Fuseki → Django (AI Service Sync)

When you create/update/delete data using **AI chat**:

1. **AI generates SPARQL query**
2. **SPARQL executes on Fuseki** first
3. **Sync function parses SPARQL** and creates Django objects
4. **Django saves to SQLite**

**Implemented for:**

- ✅ INSERT operations (create)
- ✅ DELETE operations (delete)
- ⚠️ UPDATE operations (partial - currently converts to DELETE+INSERT)

**Files:**

- `apps/ai_service/views.py`
  - `sync_insert_from_fuseki_to_django()` - Syncs AI-created data to Django
  - `sync_delete_from_fuseki_to_django()` - Syncs AI-deleted data to Django

## Supported Operations

### ✅ Fully Synced Operations

| Operation            | Django CRUD | AI Chat     | Status |
| -------------------- | ----------- | ----------- | ------ |
| Create Meal          | ✅ → Fuseki | ✅ → Django | Synced |
| Update Meal          | ✅ → Fuseki | ⚠️ Partial  | Synced |
| Delete Meal          | ✅ → Fuseki | ✅ → Django | Synced |
| Create Activity      | ✅ → Fuseki | ✅ → Django | Synced |
| Delete Activity      | ✅ → Fuseki | ✅ → Django | Synced |
| Create Habit         | ✅ → Fuseki | ✅ → Django | Synced |
| Delete Habit         | ✅ → Fuseki | ✅ → Django | Synced |
| Create Health Metric | ✅ → Fuseki | ✅ → Django | Synced |
| Delete Health Metric | ✅ → Fuseki | ✅ → Django | Synced |

## Example Workflows

### Workflow 1: Create Meal via CRUD

```
1. User fills form: "Breakfast - Oatmeal - 300 calories"
2. Django creates Meal in SQLite
3. Signal triggers: post_save(Meal)
4. Signal handler executes SPARQL INSERT to Fuseki
5. ✅ Data exists in BOTH databases
6. AI can now query this meal
```

### Workflow 2: Create Meal via AI

```
1. User types: "add breakfast meal oatmeal with 300 calories"
2. AI generates SPARQL INSERT query
3. SPARQL executes on Fuseki
4. sync_insert_from_fuseki_to_django() detects INSERT
5. Creates Meal object in Django SQLite
6. ✅ Data exists in BOTH databases
7. CRUD forms can now show this meal
```

### Workflow 3: Delete via CRUD

```
1. User clicks "Delete" on a meal
2. Django deletes Meal from SQLite
3. Signal triggers: post_delete(Meal)
4. Signal handler executes SPARQL DELETE on Fuseki
5. ✅ Data removed from BOTH databases
```

### Workflow 4: Delete via AI

```
1. User types: "delete meal oatmeal"
2. AI generates SPARQL DELETE query
3. SPARQL executes on Fuseki
4. sync_delete_from_fuseki_to_django() detects DELETE
5. Finds and deletes Meal from Django SQLite
6. ✅ Data removed from BOTH databases
```

## Technical Details

### Django Signal Handlers

Signals are registered in `apps.py` for each app:

```python
# apps/meals/apps.py
class MealsConfig(AppConfig):
    def ready(self):
        import apps.meals.signals  # Registers signal handlers
```

### SPARQL Pattern Matching

The AI sync functions use regex to parse SPARQL queries:

```python
# Meal INSERT pattern
meal_pattern = r'sh:(\w+)\s+a\s+sh:(Breakfast|Lunch|Dinner|Snack)[^}]*sh:meal_name\s+"([^"]+)"[^}]*sh:total_calories\s+(\d+)'

# Activity INSERT pattern
activity_pattern = r'sh:(\w+)\s+a\s+sh:(Cardio|Musculation|Natation)[^}]*sh:activity_name\s+"([^"]+)"'

# Habit INSERT pattern
habit_pattern = r'sh:(\w+)\s+a\s+sh:(Reading|Cooking|Drawing|Journaling)[^}]*sh:habit_name\s+"([^"]+)"'
```

### Error Handling

All sync operations are wrapped in try-catch blocks:

- **Errors are logged** but don't stop the main operation
- **Django operation continues** even if Fuseki sync fails
- **Fuseki operation continues** even if Django sync fails

This ensures the user experience is not disrupted by sync issues.

## Testing the Sync

### Test 1: Create via CRUD, Query via AI

```
1. Go to Meals page → Add "Lunch - Pasta - 400 cal"
2. Go to AI Chat → Type "show me all meals"
3. ✅ You should see "Pasta" in the results
```

### Test 2: Create via AI, View in CRUD

```
1. Go to AI Chat → Type "add dinner meal pizza with 600 calories"
2. Go to Meals page
3. ✅ You should see "Pizza" in the list
```

### Test 3: Delete via CRUD, Query via AI

```
1. Go to Meals page → Delete "Pasta"
2. Go to AI Chat → Type "show me all meals"
3. ✅ "Pasta" should NOT appear in results
```

### Test 4: Delete via AI, Check CRUD

```
1. Go to AI Chat → Type "delete meal pizza"
2. Go to Meals page
3. ✅ "Pizza" should NOT appear in the list
```

## Monitoring Sync Status

Check Django logs for sync operations:

```bash
# View logs
python manage.py runserver

# Look for log messages like:
# INFO: Meal 123 synced to Fuseki (created)
# INFO: Activity 45 synced to Fuseki (updated)
# INFO: Habit 'Reading' created in Django with ID: 7
# ERROR: Failed to sync Meal 123 to Fuseki: Connection refused
```

## Troubleshooting

### Issue: AI-created items don't appear in CRUD

**Cause**: Fuseki → Django sync may have failed

**Solution**:

1. Check if Fuseki is running: `http://localhost:3030`
2. Check Django logs for errors
3. Verify user exists in Django database
4. Try creating manually via CRUD to test

### Issue: CRUD-created items don't appear in AI queries

**Cause**: Django → Fuseki sync may have failed

**Solution**:

1. Check if Fuseki is running
2. Check Django logs for signal errors
3. Verify SPARQL endpoint is accessible
4. Test with manual SPARQL query

### Issue: "No users found in Django database"

**Cause**: No users exist for AI to assign data to

**Solution**:

1. Create a user via signup
2. Or use Django admin to create users
3. Provide `user_id` in AI requests

## Future Improvements

1. **Batch Sync**: Sync multiple items at once
2. **Conflict Resolution**: Handle cases where data differs between databases
3. **Sync Queue**: Queue sync operations for better performance
4. **Sync Dashboard**: Web UI to monitor sync status
5. **Manual Sync Tools**: Commands to manually sync all data

## Configuration

### Required Settings

```python
# settings.py
FUSEKI_ENDPOINT = 'http://localhost:3030/smarthealth'
FUSEKI_UPDATE_ENDPOINT = f'{FUSEKI_ENDPOINT}/update'
FUSEKI_QUERY_ENDPOINT = f'{FUSEKI_ENDPOINT}/query'
```

### Required Services

1. **Fuseki Server** must be running on port 3030
2. **Django Server** must be running on port 8000
3. **SQLite database** must be created with migrations

## Summary

✅ **Bi-directional sync is now active!**

- Create/Update/Delete via CRUD → Automatically syncs to Fuseki
- Create/Delete via AI → Automatically syncs to Django
- Data is consistent across both databases
- No manual sync commands needed
- Errors are handled gracefully

Your data is now unified! 🎉
