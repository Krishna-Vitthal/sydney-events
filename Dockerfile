# Root Dockerfile for Render deployment (Backend API)
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements first for better caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/app ./app

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

# Expose port (Render uses PORT env variable)
EXPOSE 10000

# Default PORT for Render, can be overridden
ENV PORT=10000

# Run the application using shell form to expand $PORT
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
