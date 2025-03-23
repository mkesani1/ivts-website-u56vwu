# Dockerfile for IndiVillage Backend Application
# Multi-stage build optimized for both production and development environments

# Stage 1: Builder stage for installing dependencies and preparing the application
FROM python:3.10-slim AS builder

# Set environment variables for Python to:
# - Prevent Python from writing .pyc files to disk
# - Prevent Python from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app

# Copy requirements files first to leverage Docker cache
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install development dependencies if building for development environment
ARG ENVIRONMENT=production
RUN if [ "$ENVIRONMENT" = "development" ]; then \
        pip install --no-cache-dir -r requirements-dev.txt; \
    fi

# Copy the rest of the application code
COPY . .

# Stage 2: Final stage with minimal runtime dependencies
FROM python:3.10-slim AS final

# Pass build argument to final stage
ARG ENVIRONMENT=production
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    ENVIRONMENT=${ENVIRONMENT} \
    WORKERS=4

# Install runtime system dependencies only
# - libpq5: PostgreSQL client library
# - curl: For health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app

# Copy installed dependencies and application code from builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

# Create non-root user for security
RUN useradd -m appuser && \
    chown -R appuser:appuser /app

# Set user to non-root
USER appuser

# Expose the port the app runs on
EXPOSE 8000

# Health check to verify application status
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=40s \
    CMD curl --fail http://localhost:8000/api/v1/health || exit 1

# Set different entrypoints based on environment:
# - Development: Use uvicorn with hot reload
# - Production: Use gunicorn with multiple workers
ENTRYPOINT ["sh", "-c", "if [ \"$ENVIRONMENT\" = \"development\" ]; then \
    uvicorn main:app --reload --host 0.0.0.0 --port ${PORT:-8000}; \
    else \
    gunicorn --bind 0.0.0.0:${PORT:-8000} --workers ${WORKERS:-4} --worker-class uvicorn.workers.UvicornWorker wsgi:application; \
    fi"]