# Smart Health Web - Semantic Web Project

A Django-based semantic web application for health management using RDFS ontology and Apache Fuseki.

## Architecture

**Front-end → AI API → SPARQL Query → Fuseki → JSON Response → Django → Front-end**

## Features

- 👥 **User Management**: Students & Teachers profiles
- 🏃 **Activity Tracking**: Cardio, Musculation, Natation with intensity levels
- 📊 **Health Records**: Comprehensive health metrics (Heart Rate, Cholesterol, Sugar Level, etc.)
- 🍽️ **Meal Tracking**: Nutrition info with calories, protein, carbs, fiber tracking
- 📝 **Habit Tracking**: Reading, Cooking, Drawing, Journaling
- 🏆 **Challenge System (Defis)**: Gamification with badges and objectives
- 🤖 **AI-Powered Queries**: Natural language processing for SPARQL generation
- 🔗 **SPARQL Integration**: Direct connection to Apache Fuseki triplestore

## Tech Stack

- **Backend**: Django 5.0 + Django REST Framework
- **Semantic Web**: RDFLib, SPARQLWrapper
- **Triplestore**: Apache Fuseki
- **Database**: SQLite (development) / PostgreSQL (production)

## Project Structure

```
Smart_Health_Web/
├── backend/              # Django project settings
├── apps/
│   ├── users/           # User, Student, Teacher models
│   ├── activities/      # Activity tracking
│   ├── health_records/  # Health metrics
│   ├── meals/           # Meal and nutrition tracking
│   ├── habits/          # Habit tracking
│   ├── defis/           # Challenge system
│   ├── sparql_service/  # SPARQL client and query builder
│   └── ai_service/      # AI prompt processor
├── ontology/            # RDFS/OWL ontology files
├── scripts/             # Utility scripts
└── static/              # Static files
```

## Setup Instructions

### 1. Clone and Setup Virtual Environment

```powershell
cd "d:\OneDrive\Bureau\Web Sementique\Smart_Health_Web"
python -m venv venv
.\venv\Scripts\activate
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```powershell
copy .env.example .env
# Edit .env with your configuration
```

### 4. Run Migrations

```powershell
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser

```powershell
python manage.py createsuperuser
```

### 6. Run Development Server

```powershell
python manage.py runserver
```

## Apache Fuseki Setup

### 1. Download and Install Fuseki

Download from: https://jena.apache.org/download/

### 2. Start Fuseki Server

```powershell
# Navigate to Fuseki directory
cd path\to\fuseki
.\fuseki-server.bat --update --mem /smarthealth
```

### 3. Upload Ontology

- Open browser: http://localhost:3030
- Create dataset: `smarthealth`
- Upload `ontology/smarthealth.ttl`

## API Endpoints

### AI Service

- `POST /api/ai/query/` - Natural language query processing

### Users

- `GET /api/users/` - List all users
- `POST /api/users/` - Create user
- `GET /api/users/{id}/` - Get user details

### Activities

- `GET /api/activities/` - List activities
- `POST /api/activities/` - Create activity
- `GET /api/activity-logs/` - List activity logs

### Health Records

- `GET /api/health-records/` - List health records
- `POST /api/health-records/` - Create health record
- `GET /api/health-metrics/` - List health metrics

### Meals

- `GET /api/meals/` - List meals
- `POST /api/meals/` - Create meal
- `GET /api/food-items/` - List food items

### Habits

- `GET /api/habits/` - List habits
- `POST /api/habits/` - Create habit
- `GET /api/habit-logs/` - List habit logs

### Defis (Challenges)

- `GET /api/defis/` - List challenges
- `POST /api/defis/` - Create challenge
- `GET /api/participations/` - List participations

## AI Query Examples

```json
POST /api/ai/query/
{
  "prompt": "Show me all activities for user 1",
  "user_id": 1
}

POST /api/ai/query/
{
  "prompt": "What are the health metrics for this user?",
  "user_id": 1
}

POST /api/ai/query/
{
  "prompt": "Show me all meals with high calories"
}
```

## Ontology Structure

The project uses an RDFS ontology with the following main classes:

- **User**: Base user class (Student, Teacher subclasses)
- **Activity**: Physical activities (Cardio, Musculation, Natation)
- **HealthRecord**: Health tracking with metrics
- **Meal**: Nutrition tracking (Breakfast, Lunch, Dinner, Snack)
- **Habit**: Personal habits (Reading, Cooking, Drawing, Journaling)
- **Defi**: Challenge system with badges and participation

## Development

### Running Tests

```powershell
python manage.py test
```

### Creating Migrations

```powershell
python manage.py makemigrations app_name
```

### Admin Panel

Access at: http://localhost:8000/admin

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Submit a pull request

## License

MIT License

## Contact

For questions or support, please open an issue on GitHub.
