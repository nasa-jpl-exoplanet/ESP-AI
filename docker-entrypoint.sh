#!/bin/bash
# ESP-AI Docker entrypoint script
# Starts Ollama service and ESP-AI API

set -e

echo "Starting ESP-AI container..."

# Start Ollama in the background
echo "Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "Waiting for Ollama to start..."
sleep 5

# Pull required models if not already present
echo "Checking for LLM models..."
if ! ollama list | grep -q "codellama"; then
    echo "Pulling codellama model..."
    ollama pull codellama
fi

if ! ollama list | grep -q "llama3.2"; then
    echo "Pulling llama3.2 model..."
    ollama pull llama3.2
fi

echo "Ollama ready!"

# Start ESP-AI API
echo "Starting ESP-AI API on port ${ESP_AI_PORT}..."
cd /app
python api/server.py

# If API exits, kill Ollama
kill $OLLAMA_PID
