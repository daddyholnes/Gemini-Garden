# Set environment variables for development
$env:ENV = "development"
$env:PYTHONPATH = "$PWD"

# Activate virtual environment if it exists and isn't already activated
if (Test-Path "venv\Scripts\Activate.ps1") {
    if (-not $env:VIRTUAL_ENV) {
        . .\venv\Scripts\Activate.ps1
    }
}

# Run the Streamlit application
streamlit run pages/01_Gemini_Studio.py