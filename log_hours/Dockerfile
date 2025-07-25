FROM mcr.microsoft.com/playwright/python:v1.53.0-jammy

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY pyproject.toml ./

# Install Poetry
RUN pip install poetry

# Configure Poetry: Don't create virtual environment inside container
RUN poetry config virtualenvs.create false

# Install Python dependencies
RUN poetry install --no-dev --no-interaction --no-ansi

# Install Playwright browsers
RUN playwright install chromium && playwright install-deps chromium

# Copy application code
COPY . .

# Create directories for volumes
RUN mkdir -p /app/screenshots /app/logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Copy entrypoint script if it exists
COPY docker-entrypoint.sh /docker-entrypoint.sh 2>/dev/null || echo "#!/bin/bash\nexec \"\$@\"" > /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Default command
CMD ["python", "-m", "pytest", "loghours.py::TestLoghours::test_loghours", "-v"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from loghours import TestLoghours; print('OK')" || exit 1

ENTRYPOINT ["/docker-entrypoint.sh"] 