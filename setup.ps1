# Smart Health Web - Automated Setup Script
# Run this script to automatically set up the project

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Smart Health Web - Automated Setup" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python is not installed or not in PATH!" -ForegroundColor Red
    Write-Host "Please install Python 3.9+ from https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Python is installed: $pythonVersion" -ForegroundColor Green

# Check if we're in the correct directory
if (-not (Test-Path "manage.py")) {
    Write-Host "ERROR: manage.py not found!" -ForegroundColor Red
    Write-Host "Please run this script from the project root directory." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Step 1: Creating Virtual Environment" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

if (Test-Path "venv") {
    Write-Host "Virtual environment already exists." -ForegroundColor Yellow
} else {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Virtual environment created successfully!" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Failed to create virtual environment!" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Step 2: Installing Dependencies" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host "Activating virtual environment and installing dependencies..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed successfully!" -ForegroundColor Green
} else {
    Write-Host "ERROR: Failed to install dependencies!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Step 3: Setting Up Environment Variables" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

if (Test-Path ".env") {
    Write-Host ".env file already exists." -ForegroundColor Yellow
} else {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✓ .env file created!" -ForegroundColor Green
    Write-Host "Note: Edit .env file if you need custom configuration." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Step 4: Database Setup" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host "Creating database migrations..." -ForegroundColor Yellow
python manage.py makemigrations
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Migrations created!" -ForegroundColor Green
} else {
    Write-Host "WARNING: Some migrations might have issues." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Applying database migrations..." -ForegroundColor Yellow
python manage.py migrate
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Database migrated successfully!" -ForegroundColor Green
} else {
    Write-Host "ERROR: Failed to migrate database!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Step 5: Creating Superuser" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Please create an admin account:" -ForegroundColor Yellow
python manage.py createsuperuser

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Green
Write-Host ""
Write-Host "1. Start Apache Fuseki (in a separate terminal):" -ForegroundColor Yellow
Write-Host "   cd C:\fuseki" -ForegroundColor White
Write-Host "   .\fuseki-server.bat --update --mem /smarthealth" -ForegroundColor White
Write-Host ""
Write-Host "2. Upload the ontology:" -ForegroundColor Yellow
Write-Host "   python scripts\import_ontology.py" -ForegroundColor White
Write-Host ""
Write-Host "3. Start the Django development server:" -ForegroundColor Yellow
Write-Host "   python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "4. Access the application:" -ForegroundColor Yellow
Write-Host "   Admin Panel: http://127.0.0.1:8000/admin" -ForegroundColor White
Write-Host "   AI Query API: http://127.0.0.1:8000/api/ai/query/" -ForegroundColor White
Write-Host ""
Write-Host "For detailed instructions, see:" -ForegroundColor Yellow
Write-Host "   - QUICKSTART.md (5-minute guide)" -ForegroundColor White
Write-Host "   - SETUP_GUIDE.md (detailed guide)" -ForegroundColor White
Write-Host "   - PROJECT_SUMMARY.md (architecture)" -ForegroundColor White
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Keep the window open
Read-Host "Press Enter to exit"
