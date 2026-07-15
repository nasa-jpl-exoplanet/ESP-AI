# ESP-AI Deployment Guide

Based on Al's instructions (July 15, 2026)

## Deployment Phases

### Phase 1: Testing on mentor0 (Current)

**Goal:** Get all components working together on the host (no Docker)

**Steps:**

#### 1. Get Access to mentor0
```bash
# SSH to mentor0
ssh enguyen@mentor0.jpl.nasa.gov
```

#### 2. Set Up Environment
```bash
# Clone ESP-AI repository
cd ~
git clone <ESP-AI-repo-url>
cd ESP-AI

# Install Python dependencies
pip install -r requirements.txt

# Install Ollama (if not already installed)
curl -fsSL https://ollama.com/install.sh | sh

# Pull LLM models
ollama pull codellama
ollama pull llama3.2
```

#### 3. Get SSL Certificates
Ask Al or JPL IT for certificates for mentor0.jpl.nasa.gov

**Following ESP's pattern:** Certificates should be at:
- `/etc/ssl/server.pem` (certificate)
- `/etc/ssl/server.key` (private key)

The API will automatically use these paths (configured via environment variables).

If certificates are elsewhere, set environment variables:
```bash
export ESP_AI_SSL_CERT=/path/to/cert.pem
export ESP_AI_SSL_KEY=/path/to/key.pem
```

#### 4. Copy EXCALIBUR Data
```bash
# Copy excalibur_runs.pkl from your local machine
scp excalibur_runs.pkl enguyen@mentor0.jpl.nasa.gov:~/ESP-AI/

# Or regenerate from backup
python scripts/extract_excalibur_from_backup.py
python scripts/convert_to_pickle.py
```

#### 5. Start Services

**Terminal 1: Start Ollama**
```bash
# Run Ollama as a service on the host
ollama serve
```

**Terminal 2: Start ESP-AI API**
```bash
cd ~/ESP-AI
python api/server.py
```

**Expected output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Loading EXCALIBUR data...
INFO:     ✓ Loaded 14103090 runs
INFO:     Application startup complete.
INFO:     Uvicorn running on https://0.0.0.0:10443
```

#### 6. Test the API

From your local machine:
```bash
# Health check
curl https://mentor0.jpl.nasa.gov:10443/api/health

# Chat test
curl -X POST https://mentor0.jpl.nasa.gov:10443/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "history": []}'

# Query test
curl -X POST https://mentor0.jpl.nasa.gov:10443/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me all JWST transit observations"}'
```

#### 7. Update Gael's Frontend

Tell Gael to update the API URL in Merlin:
```javascript
const ESP_AI_API_URL = 'https://mentor0.jpl.nasa.gov:10443/api';
```

---

### Phase 2: Production with Docker (After Testing)

**Goal:** Package everything in a Docker container on port 443

**Once Phase 1 is working:**

#### 1. Build Docker Image
```bash
cd ~/ESP-AI
docker build -t esp-ai:latest .
```

#### 2. Run with Docker Compose (Recommended)
```bash
# Set environment variables
export ESP_AI_PORT=443
export EXCALIBUR_DATA_PATH=/path/to/excalibur_runs.pkl

# Start container
docker-compose up -d
```

#### 3. Or Run Directly
```bash
docker run -d \
  --name esp-ai \
  -p 443:443 \
  -v /etc/ssl:/etc/ssl:ro \
  -v /path/to/data:/app:ro \
  -e ESP_AI_PORT=443 \
  esp-ai:latest
```

#### 4. Verify Container
```bash
# Check logs
docker logs esp-ai

# Check health
curl -k https://localhost:443/api/health

# Check running containers
docker ps
```

#### 5. Final Deployment
- Update DNS to point `excalibur.jpl.nasa.gov` to the container
- Final URL: `https://excalibur.jpl.nasa.gov/api`
- Remove port from URL (standard HTTPS port 443)

**Files Created:**
- `Dockerfile` - Container image definition
- `docker-compose.yml` - Service orchestration (following ESP pattern)
- `docker-entrypoint.sh` - Startup script for Ollama + API

**Note:** Al said we'll discover "moving parts" during testing, so Docker setup will be refined based on what we learn.

---

## Hostnames

During testing, you can use any of these (they all point to the same server):
- `mentor.jpl.nasa.gov:10443`
- `mentor0.jpl.nasa.gov:10443`
- `excalibur.jpl.nasa.gov:10443`

After Docker deployment:
- `excalibur.jpl.nasa.gov` (port 443, standard HTTPS)

---

## Port Numbers

| Phase | Port | Reason |
|-------|------|--------|
| Testing | 10443 | Must be > 10000 (Al's requirement) |
| Production | 443 | Standard HTTPS port |

---

## Running as a Service (Optional for Testing)

If you want ESP-AI to run continuously on mentor0:

### Using systemd

Create `/etc/systemd/system/esp-ai.service`:
```ini
[Unit]
Description=ESP-AI API Service
After=network.target

[Service]
Type=simple
User=enguyen
WorkingDirectory=/home/enguyen/ESP-AI
ExecStart=/usr/bin/python3 /home/enguyen/ESP-AI/api/server.py
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

Check status:
```bash
sudo systemctl status esp-ai
```

---

## Troubleshooting

### "Address already in use"
```bash
# Find what's using port 10443
sudo lsof -i :10443

# Kill the process
sudo kill -9 <PID>
```

### "Permission denied" on port 443
Ports < 1024 require root. During testing, use port > 10000.

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
curl --insecure https://mentor0.jpl.nasa.gov:10443/api/health

# Check certificate
openssl s_client -connect mentor0.jpl.nasa.gov:10443
```

---

## Next Steps

1. ✅ Get SSH access to mentor0
2. ✅ Get SSL certificates from Al/JPL IT
3. ✅ Deploy and test on mentor0:10443
4. ✅ Coordinate with Gael to update frontend
5. ⏳ Once working, create Docker container
6. ⏳ Move to port 443 and final hostname

---

## Reference

See `esp/.docker/compose.yaml` for Docker setup examples (Al's suggestion)

## Questions?

Contact Al Niessner (albert.f.niessner@jpl.nasa.gov)
