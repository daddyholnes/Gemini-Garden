FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for PyAudio and other libraries
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    python3-dev \
    gcc \
    ffmpeg \
    libsndfile1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create Streamlit config
RUN mkdir -p .streamlit && \
    echo '[server]\nheadless = true\naddress = "0.0.0.0"\nport = 8080\nenableXsrfProtection = true\nenableCORS = false\n\n[theme]\nprimaryColor = "#7B39E9"\nbackgroundColor = "#1E1E1E"\nsecondaryBackgroundColor = "#272727"\ntextColor = "#FFFFFF"' > .streamlit/config.toml

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define environment variable for port (Cloud Run uses PORT env variable)
ENV PORT 8080

# Set environment variables for security and OAuth
ENV BYPASS_STATE_CHECK true
ENV OAUTH_REDIRECT_URI https://ai-chat-studio.dartopia.uk/

# Run our custom WSGI wrapper instead of direct Streamlit command
CMD python wsgi.py