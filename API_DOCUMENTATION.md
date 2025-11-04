# Smart Health Web - API Documentation

## Overview

This document provides comprehensive documentation for all API endpoints in the Smart Health Web application. The API is built with Django REST Framework and follows RESTful principles.

## Base URL

```
http://127.0.0.1:8000/api/
```

## Authentication

Most endpoints require authentication. Include the authentication token in the Authorization header:

```
Authorization: Token <your-token>
```

## API Endpoints

### 1. Activities API (`/api/activities/`)

#### Activity Endpoints

- **List/Create Activities**: `GET/POST /api/activities/activities/`
- **Retrieve/Update/Delete Activity**: `GET/PUT/PATCH/DELETE /api/activities/activities/{id}/`
- **Get Activity Logs**: `GET /api/activities/activities/{id}/logs/`

#### Activity Log Endpoints

- **List/Create Activity Logs**: `GET/POST /api/activities/logs/`
- **Retrieve/Update/Delete Log**: `GET/PUT/PATCH/DELETE /api/activities/logs/{id}/`
- **My Logs**: `GET /api/activities/logs/my_logs/`
- **Filter by Intensity**: `GET /api/activities/logs/by_intensity/?intensity=low|medium|high`

**Example Activity Log Creation:**

```json
POST /api/activities/logs/
{
  "activity_id": 1,
  "date": "2025-11-04T10:00:00Z",
  "duration": 30,
  "intensity": "MEDIUM",
  "calories_burned": 250.0,
  "heart_rate": 120
}
```

#### Specific Activity Types

- **Cardio**: `GET/POST /api/activities/cardio/`
- **Musculation**: `GET/POST /api/activities/musculation/`
- **Natation**: `GET/POST /api/activities/natation/`

---

### 2. Habits API (`/api/habits/`)

#### Habit Endpoints

- **List/Create Habits**: `GET/POST /api/habits/habits/`
- **Retrieve/Update/Delete Habit**: `GET/PUT/PATCH/DELETE /api/habits/habits/{id}/`
- **My Habits**: `GET /api/habits/habits/my_habits/`
- **Filter by Type**: `GET /api/habits/habits/by_type/?type=reading|cooking|drawing|journaling`
- **Get Habit Logs**: `GET /api/habits/habits/{id}/logs/`

**Example Habit Creation:**

```json
POST /api/habits/habits/
{
  "habit_name": "Read 30 Minutes Daily",
  "habit_type": "READING",
  "description": "Read technical books for self-improvement"
}
```

#### Habit Log Endpoints

- **List/Create Habit Logs**: `GET/POST /api/habits/logs/`
- **Retrieve/Update/Delete Log**: `GET/PUT/PATCH/DELETE /api/habits/logs/{id}/`
- **My Logs**: `GET /api/habits/logs/my_logs/`

#### Specific Habit Types

- **Reading**: `GET/POST /api/habits/reading/`
- **Cooking**: `GET/POST /api/habits/cooking/`
- **Drawing**: `GET/POST /api/habits/drawing/`
- **Journaling**: `GET/POST /api/habits/journaling/`

---

### 3. Meals API (`/api/meals/`)

#### Meal Endpoints

- **List/Create Meals**: `GET/POST /api/meals/meals/`
- **Retrieve/Update/Delete Meal**: `GET/PUT/PATCH/DELETE /api/meals/meals/{id}/`
- **My Meals**: `GET /api/meals/meals/my_meals/`
- **Filter by Type**: `GET /api/meals/meals/by_type/?type=breakfast|lunch|dinner|snack`
- **Today's Meals**: `GET /api/meals/meals/today/`
- **Get Food Items**: `GET /api/meals/meals/{id}/food_items/`

**Example Meal Creation:**

```json
POST /api/meals/meals/
{
  "meal_name": "Healthy Breakfast",
  "meal_type": "BREAKFAST",
  "meal_date": "2025-11-04T08:00:00Z",
  "total_calories": 450
}
```

#### Food Item Endpoints

- **List/Create Food Items**: `GET/POST /api/meals/food-items/`
- **Retrieve/Update/Delete Food Item**: `GET/PUT/PATCH/DELETE /api/meals/food-items/{id}/`
- **Filter by Type**: `GET /api/meals/food-items/by_type/?type=protein|carbs|fats`

**Example Food Item Creation:**

```json
POST /api/meals/food-items/
{
  "meal": 1,
  "food_item_name": "Oatmeal",
  "food_item_description": "Whole grain oats with honey",
  "food_type": "CARBS"
}
```

#### Meal Type Endpoints (Read-only)

- **Breakfast**: `GET /api/meals/breakfast/`
- **Lunch**: `GET /api/meals/lunch/`
- **Dinner**: `GET /api/meals/dinner/`
- **Snack**: `GET /api/meals/snack/`

---

### 4. Health Records API (`/api/health-records/`)

#### Health Record Endpoints

- **List/Create Records**: `GET/POST /api/health-records/records/`
- **Retrieve/Update/Delete Record**: `GET/PUT/PATCH/DELETE /api/health-records/records/{id}/`
- **My Records**: `GET /api/health-records/records/my_records/`
- **Get Metrics**: `GET /api/health-records/records/{id}/metrics/`
- **Latest Record**: `GET /api/health-records/records/latest/`

**Example Health Record Creation:**

```json
POST /api/health-records/records/
{
  "health_record_name": "Monthly Checkup - November",
  "description": "Regular health monitoring",
  "start_date": "2025-11-01T00:00:00Z"
}
```

#### Health Metric Endpoints

- **List/Create Metrics**: `GET/POST /api/health-records/metrics/`
- **Retrieve/Update/Delete Metric**: `GET/PUT/PATCH/DELETE /api/health-records/metrics/{id}/`
- **My Metrics**: `GET /api/health-records/metrics/my_metrics/`
- **Filter by Type**: `GET /api/health-records/metrics/by_type/?type=heart_rate|cholesterol`
- **Latest by Type**: `GET /api/health-records/metrics/latest_by_type/`

**Example Health Metric Creation:**

```json
POST /api/health-records/metrics/
{
  "health_record": 1,
  "metric_name": "Heart Rate",
  "metric_value": 72.0,
  "metric_unit": "bpm",
  "metric_description": "Resting heart rate",
  "measured_at": "2025-11-04T09:00:00Z"
}
```

#### User-Specific Records

- **Student Health Records**: `GET/POST /api/health-records/student-records/`
- **Teacher Health Records**: `GET/POST /api/health-records/teacher-records/`

---

### 5. Défis (Challenges) API (`/api/defis/`)

#### Défi Endpoints

- **List/Create Challenges**: `GET/POST /api/defis/defis/`
- **Retrieve/Update/Delete Challenge**: `GET/PUT/PATCH/DELETE /api/defis/defis/{id}/`
- **Active Challenges**: `GET /api/defis/defis/active/`
- **Join Challenge**: `POST /api/defis/defis/{id}/join/`
- **Get Participants**: `GET /api/defis/defis/{id}/participants/`
- **Leaderboard**: `GET /api/defis/defis/{id}/leaderboard/`

**Example Défi Creation:**

```json
POST /api/defis/defis/
{
  "defi_name": "30-Day Fitness Challenge",
  "defi_description": "Complete 10,000 steps daily for 30 days"
}
```

#### Participation Endpoints

- **List/Create Participations**: `GET/POST /api/defis/participations/`
- **Retrieve/Update/Delete Participation**: `GET/PUT/PATCH/DELETE /api/defis/participations/{id}/`
- **My Participations**: `GET /api/defis/participations/my_participations/`
- **Active Participations**: `GET /api/defis/participations/active/`
- **Update Progress**: `POST /api/defis/participations/{id}/update_progress/`
- **Leave Challenge**: `POST /api/defis/participations/{id}/leave/`

**Example Progress Update:**

```json
POST /api/defis/participations/{id}/update_progress/
{
  "progress_value": 75
}
```

---

### 6. AI Service API (`/api/ai/`)

#### AI Query Endpoint

- **Natural Language Query**: `POST /api/ai/query/`

**Example AI Query:**

```json
POST /api/ai/query/
{
  "question": "Show me all users who have logged activities in the last week"
}
```

**Response:**

```json
{
  "sparql_query": "SELECT ?user ...",
  "results": [...],
  "execution_time": "0.5s"
}
```

---

## Response Formats

### Success Response

```json
{
  "id": 1,
  "field1": "value1",
  "field2": "value2",
  "created_at": "2025-11-04T10:00:00Z"
}
```

### Error Response

```json
{
  "error": "Error message",
  "detail": "Detailed error description"
}
```

### List Response

```json
{
  "count": 10,
  "next": "http://127.0.0.1:8000/api/activities/logs/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## Common Query Parameters

### Pagination

- `?page=2` - Get specific page
- `?page_size=50` - Set items per page

### Filtering

- `?type=breakfast` - Filter by type
- `?intensity=high` - Filter by intensity
- `?date=2025-11-04` - Filter by date

### Ordering

- `?ordering=created_at` - Order ascending
- `?ordering=-created_at` - Order descending

### Search

- `?search=keyword` - Search across fields

---

## HTTP Status Codes

- `200 OK` - Successful GET, PUT, PATCH
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Invalid data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Best Practices

1. **Always authenticate** - Include authentication credentials for protected endpoints
2. **Use appropriate HTTP methods** - GET for reading, POST for creating, PUT/PATCH for updating, DELETE for removing
3. **Handle errors gracefully** - Check response status codes and handle errors appropriately
4. **Paginate large datasets** - Use pagination parameters for better performance
5. **Filter results** - Use query parameters to get specific data
6. **Validate data** - Ensure data meets requirements before sending

---

## Testing with cURL

### Example: Create an Activity Log

```bash
curl -X POST http://127.0.0.1:8000/api/activities/logs/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{
    "activity_id": 1,
    "date": "2025-11-04T10:00:00Z",
    "duration": 30,
    "intensity": "MEDIUM"
  }'
```

### Example: Get My Meals

```bash
curl -X GET http://127.0.0.1:8000/api/meals/meals/my_meals/ \
  -H "Authorization: Token YOUR_TOKEN"
```

---

## Additional Resources

- **Django REST Framework**: https://www.django-rest-framework.org/
- **API Testing Tool**: Use Postman or Insomnia for testing
- **Admin Interface**: http://127.0.0.1:8000/admin/

---

For more information or support, please contact the development team.
