# ============================================================================
# PRODUCTION DOCKERFILE FOR AIF360 FAIRNESS API
# Optimized for Railway.app deployment with system dependencies
# ============================================================================

# Use Python 3.11 slim image (balance between size and compatibility)
FROM python:3.11-slim-bookworm

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8000

# Install system dependencies required by AIF360
# These are the CRITICAL packages that Render free tier cannot install
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Required for scipy/numpy compilation
    gcc \
    g++ \
    gfortran \
    # Required for linear algebra operations
    libblas-dev \
    liblapack-dev \
    # Required for building Python packages
    python3-dev \
    # Utilities
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first (for layer caching)
COPY requirements.txt .

# Install Python dependencies
# Use --no-cache-dir to reduce image size
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port (Railway will inject $PORT, default to 8000)
EXPOSE 8000

# Health check (Railway handles health checks externally, disable internal)
# HEALTHCHECK disabled for Railway - Railway uses external TCP checks

# Start command using Gunicorn with Uvicorn workers
# Railway injects PORT at runtime, fallback to 8000
CMD gunicorn app.main:app \
    --workers 1 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:${PORT:-8000} \
    --timeout 120 \
    --log-level info \
    --access-logfile - \
    --error-logfile -
