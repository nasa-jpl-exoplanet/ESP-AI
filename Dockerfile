# ESP-AI Dockerfile
# Based on ESP's Docker pattern from esp/.docker/compose.yaml

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for data
RUN mkdir -p /app/data

# Environment variables (can be overridden at runtime)
ENV ESP_AI_PORT=443
ENV ESP_AI_SSL_KEY=/etc/ssl/server.key
ENV ESP_AI_SSL_CERT=/etc/ssl/server.pem
ENV EXCALIBUR_DATA_PATH=/app
ENV PYTHONUNBUFFERED=1

# Expose API port
EXPOSE 443

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f -k https://localhost:443/api/health || exit 1

# Start script that launches both Ollama and the API
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
