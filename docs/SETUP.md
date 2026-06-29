# Setup Guide

Complete setup instructions for ESP-AI.

## Prerequisites

- Python 3.8+
- Ollama with models: `codellama` and `llama3.2`
- Dawgie database backup file (ops.00.sql or ops.00.bck)

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `gradio` - Web interface framework
- `ollama` - LLM interface
- `pandas` - Data manipulation
- `orjson` - Fast JSON parsing

### 2. Install Ollama Models

```bash
# For query generation (required)
ollama pull codellama

# For conversational chatbot (required)
ollama pull llama3.2
```

### 3. Prepare Data

#### Option A: From PostgreSQL Backup

```bash
# 1. Export your Dawgie database
pg_dump -U username dbname > ops.00.sql

# 2. Place ops.00.sql in the ESP-AI directory

# 3. Extract data
python scripts/extract_excalibur_from_backup.py

# 4. (Optional) Convert to pickle for 2x faster loading
python scripts/convert_to_pickle.py
```

#### Option B: Use Existing JSON/Pickle

If you already have `excalibur_runs.json` or `excalibur_runs.pkl`, place it in the ESP-AI root directory.

## Running

### Combined Interface (Recommended)

Both chatbot and query interface in one app:

```bash
python main.py
```

Opens at `http://localhost:7860`

### Chatbot Only

Conversational interface:

```bash
python main_chatbot.py
```

Opens at `http://localhost:7861`

### Query Interface Only

Direct filtering interface:

```bash
python main_advanced.py
```

Opens at `http://localhost:7860`

## Performance Tips

1. **Use pickle format** - Run `python scripts/convert_to_pickle.py` for 2x faster startup
2. **Keep data local** - Store data files on local SSD, not network drives
3. **Sufficient RAM** - 8GB+ recommended for 14M+ rows

## Troubleshooting

### "Model not found" error
```bash
ollama pull codellama
ollama pull llama3.2
```

### Slow loading
Convert JSON to pickle:
```bash
python scripts/convert_to_pickle.py
```

### No results from queries
Check that `excalibur_runs.json` or `excalibur_runs.pkl` exists in the root directory.

### Import errors
```bash
pip install -r requirements.txt --upgrade
```
