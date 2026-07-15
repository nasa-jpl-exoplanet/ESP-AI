# ESP-AI Deployment Guide

## Overview

ESP-AI can be deployed in two ways:
1. **Direct deployment** - Run on host without Docker (testing/development)
2. **Docker deployment** - Containerized production deployment

## Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com) installed
- SSL certificates for HTTPS
- EXCALIBUR data file (`excalibur_runs.pkl`)

## Direct Deployment (Testing)

### 1. Install Dependencies

```bash
cd ESP-AI
pip install -r requirements.txt
```

### 2. Install and Configure Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull required models
ollama pull codellama
ollama pull llama3.2

# Start Ollama service
ollama serve
```

### 3. Configure SSL Certificates

Set environment variables to point to your SSL certificates:

```bash
export ESP_AI_SSL_CERT=/path/to/cert.pem
export ESP_AI_SSL_KEY=/path/to/key.pem
export ESP_AI_PORT=10443  # Or your preferred port
```

### 4. Start the API

```bash
python3 api/server.py
```

The API will be available at `https://your-host:10443`

### 5. Test the Deployment

```bash
# Health check
curl https://your-host:10443/api/health

# Chat test
curl -X POST https://your-host:10443/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "history": []}'
```

## Docker Deployment (Production)

### 1. Build Docker Image

```bash
docker build -t esp-ai:latest .
```

### 2. Run with Docker Compose

```bash
# Set environment variables
export ESP_AI_PORT=443
export EXCALIBUR_DATA_PATH=/path/to/data

# Start container
docker-compose up -d
```

### 3. Or Run Directly

```bash
docker run -d \
  --name esp-ai \
  -p 443:443 \
  -v /etc/ssl:/etc/ssl:ro \
  -v /path/to/data:/app:ro \
  -e ESP_AI_PORT=443 \
  esp-ai:latest
```

### 4. Verify Container

```bash
# Check logs
docker logs esp-ai

# Check health
curl -k https://localhost:443/api/health

# Check running containers
docker ps
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ESP_AI_PORT` | `10443` | API port (testing: >10000, production: 443) |
| `ESP_AI_SSL_CERT` | `/etc/ssl/server.pem` | SSL certificate path |
| `ESP_AI_SSL_KEY` | `/etc/ssl/server.key` | SSL private key path |
| `ESP_AI_DEV_MODE` | `false` | Set to `true` for HTTP (no SSL) |
| `EXCALIBUR_DATA_PATH` | `/app` | Path to data directory |

### Development Mode (No SSL)

For local testing without SSL:

```bash
ESP_AI_DEV_MODE=true python3 api/server.py
```

This runs on HTTP port 8000 (no certificates needed).

## Running as a Service

### Using systemd

Create `/etc/systemd/system/esp-ai.service`:

```ini
[Unit]
Description=ESP-AI API Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/ESP-AI
Environment="ESP_AI_PORT=10443"
Environment="ESP_AI_SSL_CERT=/etc/ssl/server.pem"
Environment="ESP_AI_SSL_KEY=/etc/ssl/server.key"
ExecStart=/usr/bin/python3 /path/to/ESP-AI/api/server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl start esp-ai
sudo systemctl enable esp-ai  # Auto-start on boot
```

## Troubleshooting

### "Address already in use"

```bash
# Find what's using the port
sudo lsof -i :10443

# Kill the process
sudo kill -9 <PID>
```

### "Cannot connect to Ollama"

```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama
ollama serve
```

### SSL certificate errors

```bash
# Test with curl (ignore cert validation)
curl --insecure https://localhost:10443/api/health

# Check certificate
openssl s_client -connect localhost:10443
```

### "Permission denied" on port 443

Ports < 1024 require root privileges. Either:
- Run with sudo (not recommended)
- Use port > 1024 (e.g., 10443)
- Configure port forwarding (e.g., iptables, nginx)

## Security Considerations

- Always use HTTPS in production
- Keep SSL certificates secure and up-to-date
- Restrict API access with firewall rules
- Monitor logs for suspicious activity
- Keep Ollama and dependencies updated

## Performance Tuning

- Use pickle format for data (2x faster than JSON)
- Allocate sufficient memory for LLM models (8GB+ recommended)
- Consider using SSD storage for model files
- Monitor CPU/memory usage and adjust resources as needed
