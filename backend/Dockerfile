# Use Python 3.11 as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /workspace

# Install system dependencies including PostgreSQL client libraries
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    build-essential \
    libpq-dev \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements*.txt /workspace/backend/

# Install Python dependencies
RUN pip install --no-cache-dir -r /workspace/backend/requirements.txt

# Create necessary directories
RUN mkdir -p /workspace/backend/uploads /workspace/backend/tmp_uploads /workspace/data

# Copy application code
COPY . /workspace/backend/

# Set environment variables
ENV PYTHONPATH=/workspace
ENV FLASK_APP=app_unified.py
ENV FLASK_ENV=development

# Set working directory to backend
WORKDIR /workspace/backend

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1

# Default command
CMD ["python3", "app_unified.py"]
