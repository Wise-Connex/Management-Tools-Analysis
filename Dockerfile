# Multi-stage Dockerfile for Dash Dashboard Production Deployment
# Optimized for Dokploy platform

# ============================================================================
# Stage 1: Builder - Compile dependencies and create wheels
# ============================================================================
FROM python:3.11-slim as builder

LABEL stage=builder
LABEL description="Build stage for compiling Python dependencies"

WORKDIR /build

# Install build dependencies including BLAS/LAPACK and cmake for scipy
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    pkg-config \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY dashboard_app/requirements.txt .

# Build wheels for all dependencies (faster installation in runtime stage)
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# ============================================================================
# Stage 2: Runtime - Minimal production image
# ============================================================================
FROM python:3.11-slim

LABEL maintainer="Dimar Añez <contact@wiseconnex.com>"
LABEL description="Management Tools Analysis Dashboard - Production"
LABEL version="1.0.0"

# Install runtime dependencies including OpenMP for scikit-learn
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    libopenblas0 \
    liblapack3 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN useradd -m -u 1000 -s /bin/bash dashuser

# Set working directory
WORKDIR /app

# Copy wheels from builder stage
COPY --from=builder /wheels /wheels

# Install dependencies from pre-built wheels
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels

# Install gunicorn for production serving
RUN pip install --no-cache-dir gunicorn==21.2.0 gevent==23.9.1

# Copy application code with proper ownership
COPY --chown=dashuser:dashuser dashboard_app/ ./dashboard_app/
COPY --chown=dashuser:dashuser assets/ ./assets/
COPY --chown=dashuser:dashuser database.py ./
COPY --chown=dashuser:dashuser tools.py ./
COPY --chown=dashuser:dashuser config.py ./
COPY --chown=dashuser:dashuser dashboard_app/fix_source_mapping.py ./

# Copy configuration and scripts
COPY --chown=dashuser:dashuser config/ ./config/
COPY --chown=dashuser:dashuser gunicorn.conf.py ./
COPY --chown=dashuser:dashuser healthcheck.sh ./
COPY --chown=dashuser:dashuser entrypoint.sh ./
COPY --chown=dashuser:dashuser wsgi.py ./

# Make scripts executable
RUN chmod +x healthcheck.sh entrypoint.sh

# Create logs directory
RUN mkdir -p /app/logs && chown dashuser:dashuser /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8050 \
    FLASK_ENV=production

# Switch to non-root user
USER dashuser

# Expose application port
EXPOSE 8050

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD ./healthcheck.sh

# Use entrypoint script for initialization
ENTRYPOINT ["./entrypoint.sh"]

# Default command: run with gunicorn using WSGI entry point
CMD ["gunicorn", "-c", "gunicorn.conf.py", "wsgi:application"]