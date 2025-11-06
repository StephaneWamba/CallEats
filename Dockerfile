FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend_2/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend_2/restaurant_voice_assistant ./restaurant_voice_assistant
COPY backend_2/config ./config

# Expose port (Railway sets PORT env var)
EXPOSE 8000

# Run the application
# Railway sets PORT env var, so we use it dynamically
# Using shell form to allow variable expansion
# Enable reload if ENVIRONMENT=development (for faster iteration)
CMD if [ "$ENVIRONMENT" = "development" ]; then \
    uvicorn restaurant_voice_assistant.main:app --host 0.0.0.0 --port ${PORT:-8000} --reload; \
    else \
    uvicorn restaurant_voice_assistant.main:app --host 0.0.0.0 --port ${PORT:-8000}; \
    fi

