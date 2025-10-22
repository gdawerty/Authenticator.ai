# Use Python 3.11 as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    unixodbc \
    unixodbc-dev \
    gcc \
    g++ \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements*.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p uploads tmp_uploads data

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=app_unified_sqlserver.py
ENV FLASK_ENV=development

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1

# Default command
CMD ["python3", "app_unified_sqlserver.py"]
