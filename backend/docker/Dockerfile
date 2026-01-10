# Multi-stage build for production optimization
# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies to /app/.venv
COPY requirements.txt .
RUN python -m venv /app/.venv && \
    /app/.venv/bin/pip install --no-cache-dir --upgrade pip && \
    /app/.venv/bin/pip install --no-cache-dir -r requirements.txt

# Clean up pip cache
RUN /app/.venv/bin/pip cache purge

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy requirements and ensure all dependencies are installed
COPY requirements.txt /app/requirements.txt

# Reinstall dependencies to ensure everything is properly installed
# This is a safety measure in case something was missed in builder stage
RUN /app/.venv/bin/pip install --no-cache-dir --upgrade pip && \
    /app/.venv/bin/pip install --no-cache-dir -r /app/requirements.txt

# Set environment variables
ENV PATH=/app/.venv/bin:$PATH \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENVIRONMENT=production \
    PORT=5000

# Copy application code BEFORE creating user (as root)
# This ensures proper structure and permissions
COPY src/ /app/src/

# Verify src module structure exists
RUN ls -la /app/src/ && \
    test -f /app/src/__init__.py && \
    test -f /app/src/app.py && \
    echo "Source files verified"

# Create non-root user for security and change ownership
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Expose port
EXPOSE 5000

# Run application with gunicorn
# PYTHONPATH is already set in ENV, so it will be available
CMD /app/.venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 --worker-class sync --timeout 30 --access-logfile - --error-logfile - src.app:app