# Use Python 3.11 slim image
FROM python:3.11-slim

# Add labels for better image management
LABEL maintainer="work-logger"
LABEL description="Automated Work Logger with Jira Integration"
LABEL version="1.0"

# Set working directory
WORKDIR /app

# Install system dependencies for Playwright and cron
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    cron \
    sudo \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium \
    && playwright install-deps chromium

# Copy application code
COPY . .

# Create directories and set permissions
RUN mkdir -p screenshots logs \
    && useradd -m -s /bin/bash appuser \
    && chown -R appuser:appuser /app \
    && chown -R appuser:appuser /ms-playwright \
    && chmod +x docker-entrypoint.sh

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "from src.loghours import AutomatedWorkLogger; print('✅ Health check passed')" || exit 1

# Use entrypoint script
ENTRYPOINT ["./docker-entrypoint.sh"] 