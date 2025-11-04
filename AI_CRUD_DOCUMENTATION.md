# Smart Health AI Assistant - Complete CRUD Operations

## 🤖 Overview

The Smart Health AI Assistant now supports full CRUD (Create, Read, Update, Delete) operations on the database using natural language commands powered by Google Gemini AI.

---

## ✨ Capabilities

### 1. **Query Data (SELECT)**
Ask questions to retrieve data from the knowledge base.

**Examples:**
```
- Show me all users
- What are the activities?
- List all health metrics
- Show meals for user 1
- What challenges are available?
- Display all habits
```

### 2. **Insert Data (CREATE)**
Add new data to the knowledge base using natural language.

**Examples:**
```
- Add a new user named Alice with email alice@example.com
- Create a cardio activity called Running
- Add a breakfast meal with 500 calories
- Create a new challenge called 30-Day Fitness
- Insert a health record for user John
- Add a habit called Daily Reading
```

### 3. **Update Data (MODIFY)**
Modify existing data in the knowledge base.

**Examples:**
```
- Update user Alice email to newalice@example.com
- Change Running activity duration to 45 minutes
- Set breakfast meal calories to 600
- Modify challenge 30-Day Fitness description
- Update health metric heart rate to 72
```

### 4. **Delete Data (REMOVE)**
Remove data from the knowledge base.

**Examples:**
```
- Delete user Alice
- Remove activity Running
- Delete the breakfast meal
- Remove challenge 30-Day Fitness
- Delete health record for user John
```

---

## 🔧 How It Works

### Architecture

```
User Input (Natural Language)
    ↓
Google Gemini AI
    ↓
Intent Analysis (query/insert/update/delete)
    ↓
Entity Extraction (users, values, etc.)
    ↓
SPARQL Query Generation
    ↓
Apache Fuseki Execution
    ↓
Results/Confirmation
```

### Intent Detection

The AI automatically detects the intent from your prompt:
- **Query**: Keywords like "show", "list", "what", "display"
- **Insert**: Keywords like "add", "create", "insert", "new"
- **Update**: Keywords like "update", "change", "modify", "set"
- **Delete**: Keywords like "delete", "remove", "drop"

### Entity Extraction

The AI extracts relevant information:
- User IDs and usernames
- Email addresses
- Numbers (calories, duration, etc.)
- Entity types (user, activity, meal, etc.)
- Property values

---

## 📝 SPARQL Examples

### SELECT Query
**Natural Language:** "Show me all users"

**Generated SPARQL:**
```sparql
PREFIX sh: <http://dhia.org/ontologies/smarthealth#>

SELECT ?user ?username ?email
WHERE {
  ?user a sh:User .
  OPTIONAL { ?user sh:username ?username }
  OPTIONAL { ?user sh:email ?email }
}
```

### INSERT Query
**Natural Language:** "Add a new user named Alice with email alice@example.com"

**Generated SPARQL:**
```sparql
PREFIX sh: <http://dhia.org/ontologies/smarthealth#>

INSERT DATA {
  sh:User_Alice a sh:User ;
    sh:username "Alice" ;
    sh:email "alice@example.com" .
}
```

### UPDATE Query
**Natural Language:** "Update user Alice email to newalice@example.com"

**Generated SPARQL:**
```sparql
PREFIX sh: <http://dhia.org/ontologies/smarthealth#>

DELETE { ?u sh:email ?old }
INSERT { ?u sh:email "newalice@example.com" }
WHERE {
  ?u a sh:User ;
     sh:username "Alice" ;
     sh:email ?old
}
```

### DELETE Query
**Natural Language:** "Delete user Alice"

**Generated SPARQL:**
```sparql
PREFIX sh: <http://dhia.org/ontologies/smarthealth#>

DELETE WHERE {
  ?u a sh:User ;
     sh:username "Alice" .
  ?u ?p ?o
}
```

---

## 🎯 Use Cases

### Healthcare Data Management

1. **Patient Records**
   ```
   Add a new student named John with class "CS101"
   Update student John class to "CS102"
   Show all students
   Delete student John
   ```

2. **Activity Tracking**
   ```
   Create a cardio activity called Morning Run with 250 calories burned
   Update Morning Run activity calories to 300
   Show all activities
   Remove activity Morning Run
   ```

3. **Meal Planning**
   ```
   Add a lunch meal with 800 calories
   Create a breakfast with eggs and toast
   Update lunch meal calories to 750
   Delete the dinner meal
   ```

4. **Health Metrics**
   ```
   Add a heart rate metric with value 72 bpm
   Create a cholesterol record with value 180 mg/dL
   Update heart rate to 75 bpm
   Show all health metrics
   ```

---

## 🚀 API Usage

### Endpoint
```
POST http://127.0.0.1:8000/api/ai/query/
```

### Request Body
```json
{
  "prompt": "Your natural language command",
  "user_id": 1  // Optional
}
```

### Response for SELECT
```json
{
  "success": true,
  "prompt": "Show me all users",
  "intent": "query",
  "action": "query",
  "sparql_query": "PREFIX sh: <...> SELECT ...",
  "results_count": 5,
  "results": [...],
  "ai_powered": true,
  "ai_model": "Google Gemini Pro"
}
```

### Response for INSERT/UPDATE/DELETE
```json
{
  "success": true,
  "prompt": "Add user Alice",
  "intent": "insert",
  "action": "insert",
  "sparql_query": "PREFIX sh: <...> INSERT DATA {...}",
  "message": "Data inserted successfully",
  "ai_powered": true,
  "ai_model": "Google Gemini Pro"
}
```

---

## 🔐 Security Considerations

### Current Implementation
- No authentication required (for testing)
- All operations allowed
- Direct database access

### Production Recommendations

1. **Add Authentication**
   ```python
   permission_classes = [IsAuthenticated]
   ```

2. **Role-Based Access Control**
   - Query: All authenticated users
   - Insert: Users with "create" permission
   - Update: Users with "modify" permission
   - Delete: Admin users only

3. **Input Validation**
   - Sanitize user inputs
   - Validate SPARQL queries
   - Prevent SPARQL injection

4. **Audit Logging**
   - Log all modification operations
   - Track user actions
   - Maintain change history

5. **Rate Limiting**
   - Limit requests per user
   - Prevent abuse
   - Monitor usage

---

## 🧪 Testing

### Using cURL

**Query Example:**
```bash
curl -X POST http://127.0.0.1:8000/api/ai/query/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Show me all users"}'
```

**Insert Example:**
```bash
curl -X POST http://127.0.0.1:8000/api/ai/query/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Add a new user named Bob with email bob@test.com"}'
```

**Update Example:**
```bash
curl -X POST http://127.0.0.1:8000/api/ai/query/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Update user Bob email to newbob@test.com"}'
```

**Delete Example:**
```bash
curl -X POST http://127.0.0.1:8000/api/ai/query/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Delete user Bob"}'
```

### Using Python

```python
import requests

url = "http://127.0.0.1:8000/api/ai/query/"

# Query
response = requests.post(url, json={"prompt": "Show me all users"})
print(response.json())

# Insert
response = requests.post(url, json={
    "prompt": "Add a new user named Charlie with email charlie@example.com"
})
print(response.json())

# Update
response = requests.post(url, json={
    "prompt": "Update user Charlie email to newcharlie@example.com"
})
print(response.json())

# Delete
response = requests.post(url, json={"prompt": "Delete user Charlie"})
print(response.json())
```

---

## 💡 Best Practices

1. **Be Specific**
   - ✅ "Add a new user named Alice with email alice@example.com"
   - ❌ "Add user"

2. **Use Clear Actions**
   - Use action words: add, create, update, change, delete, remove
   - Be explicit about what you want to modify

3. **Include Identifiers**
   - Reference entities by name or ID
   - Example: "Update user Alice" or "Delete activity with ID 5"

4. **Check Results**
   - Always verify successful operations
   - Query data after modifications to confirm changes

5. **Start with Queries**
   - Test with SELECT queries first
   - Understand data structure before modifications

---

## 🐛 Troubleshooting

### AI Service Not Configured
**Error:** "AI service not configured"

**Solution:**
1. Get API key from https://makersuite.google.com/app/apikey
2. Add to `.env` file: `GEMINI_API_KEY=your_key_here`
3. Restart Django server

### Invalid SPARQL Query
**Error:** "Failed to execute modification query"

**Solution:**
- Check the generated SPARQL query
- Verify entity exists before updating/deleting
- Ensure proper syntax in natural language input

### No Results
**Issue:** Query returns 0 results

**Solution:**
- Verify data exists in knowledge base
- Check entity names and IDs
- Try broader queries first

---

## 📊 Monitoring

### Track Operations

Monitor AI operations in Django logs:
```python
# In views.py
import logging
logger = logging.getLogger(__name__)

logger.info(f"AI Operation: {intent} - User: {user_id} - Prompt: {prompt}")
```

### View SPARQL Queries

All generated SPARQL queries are returned in the API response:
```json
{
  "sparql_query": "PREFIX sh: <...> ..."
}
```

---

## 🎓 Learning Path

1. **Start with Queries** - Learn to retrieve data
2. **Try Inserts** - Add simple entities
3. **Practice Updates** - Modify existing data
4. **Test Deletes** - Remove data safely
5. **Combine Operations** - Complex workflows

---

## 🚀 Future Enhancements

- [ ] Batch operations (multiple inserts at once)
- [ ] Transaction support (rollback on error)
- [ ] Natural language joins (complex queries)
- [ ] Conditional updates (IF conditions)
- [ ] Data validation before modifications
- [ ] Change history tracking
- [ ] Automated backups before deletes
- [ ] AI-suggested corrections for errors

---

## 📞 Support

For issues or questions:
1. Check API_DOCUMENTATION.md
2. Review SPARQL query examples
3. Test with simple examples first
4. Check Django logs for errors

---

**Powered by Google Gemini AI + Apache Jena Fuseki** 🚀
