# PowerShell script to prepare Gemini Garden for Docker Desktop
Write-Host "Preparing Gemini Garden for Docker Desktop..." -ForegroundColor Green

# Check if Docker Desktop is running
$dockerRunning = Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue
if (-not $dockerRunning) {
    Write-Host "⚠️ Docker Desktop doesn't appear to be running. Please start Docker Desktop first." -ForegroundColor Yellow
    Write-Host "   After starting Docker Desktop, run this script again." -ForegroundColor Yellow
    exit
}

# Check for .env file
if (-not (Test-Path -Path ".\.env")) {
    Write-Host "❌ .env file not found. Please ensure your environment variables are set up." -ForegroundColor Red
    exit
}

Write-Host "✅ .env file found" -ForegroundColor Green

# Check for service account file
if (-not (Test-Path -Path ".\camera-calibration-beta-51a46d9d1055.json")) {
    Write-Host "❌ Service account file not found. Please ensure your Google Cloud credentials are available." -ForegroundColor Red
    exit
}

Write-Host "✅ Service account file found" -ForegroundColor Green

# Create the secrets directory if it doesn't exist
if (-not (Test-Path -Path ".\secrets")) {
    New-Item -ItemType Directory -Path ".\secrets" | Out-Null
    Write-Host "✅ Created secrets directory" -ForegroundColor Green
}

# Run security checks
Write-Host "`nRunning security checks..." -ForegroundColor Cyan
python .\utils\security_checks.py

# Verify Docker is running
try {
    docker info | Out-Null
    Write-Host "`n✅ Docker is running and accessible" -ForegroundColor Green
}
catch {
    Write-Host "❌ Docker is not responding. Please make sure Docker Desktop is running properly." -ForegroundColor Red
    exit
}

# Ready to build and run
Write-Host "`n=========================================================" -ForegroundColor Cyan
Write-Host "Your Gemini Garden is ready for Docker Desktop!" -ForegroundColor Green
Write-Host "To build and run your containers, execute:" -ForegroundColor Cyan
Write-Host "docker-compose up --build" -ForegroundColor Yellow
Write-Host "`nTo run in detached mode (background):" -ForegroundColor Cyan
Write-Host "docker-compose up --build -d" -ForegroundColor Yellow
Write-Host "`nTo view logs when running in detached mode:" -ForegroundColor Cyan
Write-Host "docker-compose logs -f" -ForegroundColor Yellow
Write-Host "`nYour application will be available at:" -ForegroundColor Cyan
Write-Host "http://localhost:8501" -ForegroundColor Green
Write-Host "=========================================================" -ForegroundColor Cyan