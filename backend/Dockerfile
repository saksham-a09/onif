FROM python:3.12-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
# - gcc, libpq-dev: for psycopg2
# - libjpeg-dev, zlib1g-dev: for Pillow image support (deposit proof uploads)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        libjpeg-dev \
        zlib1g-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (separate layer for better caching)
COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project source
COPY . /app/

# Create directories that Django needs at runtime
RUN mkdir -p /app/static /app/media /app/logs

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Expose the application port
EXPOSE 8000

# Default entrypoint (runs migrations, collectstatic, then the CMD)
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command: production Gunicorn server
# Override in docker-compose for dev (python manage.py runserver)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
