# AI Service Setup Guide

## Problem: "AI service not configured" Error

If you see the error "AI service not configured" or a 503 Service Unavailable error, it means the Gemini API key is not set up.

## Quick Setup

### Step 1: Get Your Free Gemini API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key" or "Get API Key"
4. Copy your API key

### Step 2: Create .env File

1. In the project root directory (`Smart_Health_WebSemantique`), create a file named `.env`
2. Add the following line to the file:

```
GEMINI_API_KEY=your_actual_api_key_here
```

**Important:** Replace `your_actual_api_key_here` with your actual API key from Step 1.

### Step 3: Restart Django Server

After creating/updating the `.env` file, you must restart your Django development server:

1. Stop the server (Ctrl+C in the terminal)
2. Start it again: `python manage.py runserver`

## Complete .env File Example

Your `.env` file should look like this:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,testserver

# Gemini AI API Key (Required for AI features)
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Fuseki Configuration
FUSEKI_ENDPOINT=http://localhost:3030/smarthealth/sparql
FUSEKI_UPDATE_ENDPOINT=http://localhost:3030/smarthealth/update
```

## Verification

After setting up the `.env` file:

1. Restart the Django server
2. Visit: http://127.0.0.1:8000/api/ai/test/
3. The warning banner should disappear
4. Try submitting a query like "Show me all users"

## Troubleshooting

### Issue: Still getting "AI service not configured"

- **Check 1:** Make sure the `.env` file is in the project root (same directory as `manage.py`)
- **Check 2:** Verify the file is named exactly `.env` (not `.env.txt` or `env.txt`)
- **Check 3:** Make sure there are no spaces around the `=` sign: `GEMINI_API_KEY=your_key`
- **Check 4:** Restart the Django server after creating/updating `.env`

### Issue: API key not working

- Verify your API key is correct (copy-paste to avoid typos)
- Check that your API key hasn't expired
- Make sure you're using a valid Gemini API key (not a different Google API key)

### Issue: .env file not being read

- Make sure `python-dotenv` is installed: `pip install python-dotenv`
- Check that `load_dotenv()` is called in `settings.py` (it should be there by default)

## Testing the Configuration

You can test if the AI service is configured correctly by running:

```powershell
python test_setup.py
```

This will check:
- ✅ If GEMINI_API_KEY is found in .env
- ✅ If Fuseki is running
- ✅ If Gemini AI is enabled

## Notes

- The `.env` file should NOT be committed to git (it's in `.gitignore`)
- Keep your API key secret and don't share it publicly
- The Gemini API has free tier limits - check the documentation for details

## Additional Resources

- Gemini API Documentation: https://ai.google.dev/docs
- Get API Key: https://makersuite.google.com/app/apikey
- Django Environment Variables: https://docs.djangoproject.com/en/stable/topics/settings/#using-environment-variables

