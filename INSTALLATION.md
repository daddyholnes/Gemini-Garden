# 🚀 Installation Guide for AI Chat Studio

This guide provides detailed instructions for setting up and running the AI Chat Studio application with ease.

## 💻 One-Click Installation on Replit

The fastest way to get AI Chat Studio running is through Replit:

1. **Click the Run on Replit button:**  
   [![Run on Replit](https://replit.com/badge/github/daddyholnes/Gems-Podplai-Studio)](https://replit.com/github/daddyholnes/Gems-Podplai-Studio)

2. **Set up API keys as Replit Secrets:**
   - Click on "Secrets" in the tools panel
   - Add the following keys (only add the ones you plan to use):
     ```
     OPENAI_API_KEY=your_openai_api_key
     ANTHROPIC_API_KEY=your_anthropic_api_key
     GEMINI_API_KEY=your_gemini_api_key
     PERPLEXITY_API_KEY=your_perplexity_api_key
     # Add GOOGLE_APPLICATION_CREDENTIALS if using GCS/Vertex locally with a service account key
     # GCS_BUCKET_NAME=your_gcs_bucket_name (if implementing GCS history)
     ```

3. **Run the application:**
   - Click the "Run" button
   - Replit will automatically install all required dependencies
   - Your AI Chat Studio will be accessible at the provided URL

## 🖥️ Local Installation

### Prerequisites

- Python 3.11 or higher
- Git
- Audio capabilities require:
  - Windows: No additional steps usually needed.
  - macOS: PortAudio (`brew install portaudio`)
  - Linux: Python development files and PortAudio (`sudo apt-get install python3-dev portaudio19-dev`)

### Step 1: Clone the Repository

```bash
git clone https://github.com/daddyholnes/Gemini-Garden.git # Ensure this is the correct repo name
cd Gemini-Garden
```

### Step 2: Set Up a Virtual Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Install all required packages from the standard requirements file
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables

Create a `.env` file in the root directory (`Gemini-Garden/.env`):

```dotenv
# Required API Keys (only add the ones you plan to use)
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GEMINI_API_KEY=your_gemini_api_key
PERPLEXITY_API_KEY=your_perplexity_api_key

# Google Cloud Storage Bucket (Required for GCS History Persistence)
GCS_BUCKET_NAME=your-gcs-bucket-name

# Google Application Credentials (for local GCS/Vertex AI access)
# Set this if you are running locally and using a downloaded service account key
# GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json 

# PostgreSQL Database (Optional - GCS is the primary method being implemented)
# DATABASE_URL=postgresql://username:password@hostname:port/database

# Google OAuth Credentials (Optional - for user login)
# GOOGLE_CLIENT_ID=your_client_id
# GOOGLE_CLIENT_SECRET=your_client_secret
# OAUTH_REDIRECT_URI=http://localhost:8501 # Adjust port if needed
# APPROVED_EMAILS=your_email@example.com,another_email@example.com
# ADMIN_EMAILS=your_admin_email@example.com
```

**Important:** Add `.env` to your `.gitignore` file to prevent committing secrets!

### Step 5: Google Cloud Setup (for GCS History & Vertex AI)

1.  **Create/Select Project:** Go to the [Google Cloud Console](https://console.cloud.google.com/) and create or select a project.
2.  **Enable APIs:** Enable the "Cloud Storage" API and optionally the "Vertex AI" API.
3.  **Create GCS Bucket:** Create a Google Cloud Storage bucket to store chat histories. Note down the bucket name and add it to your `.env` file (`GCS_BUCKET_NAME`).
4.  **Authentication (Local Development):**
    *   Create a Service Account: Go to "IAM & Admin" > "Service Accounts". Create a service account.
    *   Grant Roles: Grant the service account necessary roles (e.g., `Storage Object Admin` for GCS, `Vertex AI User` for Vertex AI).
    *   Create Key: Create a JSON key for the service account and download it.
    *   Save Key: Save the key file (e.g., as `service-account-key.json`) in your project's root directory.
    *   Set Environment Variable: Uncomment and set `GOOGLE_APPLICATION_CREDENTIALS` in your `.env` file to point to the key file (`./service-account-key.json`).
    *   **Note:** When deployed on GCP (Cloud Run/App Engine), you typically grant roles to the compute service account instead of using key files.

### Step 6: Run the Application

```bash
streamlit run app.py
```

The application should be accessible, often at `http://localhost:8501` (Streamlit's default port).

--(Other sections like Mobile Setup, PostgreSQL, Voice Commands, Troubleshooting, Authentication Setup, Security, Deployment Options remain largely the same but should be reviewed for accuracy once features are fully implemented)--
