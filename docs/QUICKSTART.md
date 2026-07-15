# ESP-AI Quick Start

Get ESP-AI running in 5 minutes.

## Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com) installed
- EXCALIBUR data file (`excalibur_runs.pkl` or `excalibur_runs.json`)

## Installation

```bash
# Clone repository
git clone <repo-url>
cd ESP-AI

# Install dependencies
pip install -r requirements.txt

# Pull LLM models
ollama pull codellama
ollama pull llama3.2
```

## Running Locally

### Option 1: Development Mode (Recommended for Testing)

```bash
# Start API in development mode (HTTP, no SSL)
ESP_AI_DEV_MODE=true python3 api/server.py
```

Visit: http://localhost:8000/docs (automatic API documentation)

Test endpoints:
```bash
# Health check
curl http://localhost:8000/api/health

# Chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me all JWST data", "history": []}'
```

### Option 2: Original Gradio Interfaces

**Combined interface (chatbot + query):**
```bash
python3 main.py
```
Visit: http://localhost:7860

**Chatbot only:**
```bash
python3 main_chatbot.py
```
Visit: http://localhost:7861

**Query interface only:**
```bash
python3 main_advanced.py
```
Visit: http://localhost:7860

## What You Can Do

### Natural Language Queries

```
"Show me all JWST transit observations"
"Find HST data for GJ 436"
"What are the most recent whitelight runs?"
"List all eclipse observations"
"Show me atmospheric modeling runs for WASP-12"
```

### Conversational Chat

```
"Hello!"
"What can you do?"
"Call me Elizabeth"
"How many observations do we have?"
```

## Next Steps

- **Deploy to mentor0:** See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Integrate with frontend:** See [FRONTEND_INTEGRATION.md](FRONTEND_INTEGRATION.md)
- **API reference:** See [api/README.md](../api/README.md)

## Troubleshooting

**"Model not found"**
```bash
ollama pull codellama
ollama pull llama3.2
```

**"Cannot connect to Ollama"**
```bash
# Start Ollama service
ollama serve
```

**"No data loaded"**
- Make sure `excalibur_runs.pkl` or `excalibur_runs.json` is in the ESP-AI directory
- Check the path in `data/load_excalibur_data.py`
