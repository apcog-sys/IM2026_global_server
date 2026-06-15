# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY CA_management/requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy CA management files
COPY CA_management/ /app/CA_management/
COPY CA_management/pki/ /app/CA_management/pki/

# Create necessary directories
RUN mkdir -p /app/CA_management/pki/certs /app/CA_management/pki/keys

# Expose port 9002
EXPOSE 9002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:9002/health')" || exit 1

# Run the CA service
CMD ["python", "-m", "uvicorn", "CA_management.ca_service:app", "--host", "0.0.0.0", "--port", "9002", "--reload"]
