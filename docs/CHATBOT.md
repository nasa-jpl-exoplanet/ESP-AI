# EXCALIBUR Chatbot Interface

A conversational AI assistant for the EXCALIBUR exoplanet spectroscopy pipeline.

## Features

- **Conversational**: Say "hello", ask "what can you do?", have natural conversations
- **Database Queries**: Ask questions like "show me all JWST transit runs"
- **Smart Detection**: Automatically detects if you want to chat or query the database
- **Friendly Responses**: Get results in readable format with context

## Quick Start

### Option 1: Chatbot Only
```bash
python main_chatbot.py
```
Access at: http://localhost:7861

### Option 2: Combined Interface (Chatbot + Query)
```bash
python main.py
```
Access at: http://localhost:7860

### Option 3: Choose Mode
```bash
# Chatbot mode
python main.py chatbot

# Query mode (original interface)
python main.py query
```

## Example Conversations

### General Chat
```
You: Hello!
Bot: Hello! I'm the EXCALIBUR assistant. I can help you query the 
     exoplanet database or answer questions about the pipeline. 
     What would you like to know?

You: What can you do?
Bot: I can help you with:
     1. Database queries: "Show me all JWST transit observations"
     2. General questions: Ask about EXCALIBUR or exoplanets
```

### Database Queries
```
You: Show me all JWST transit observations
Bot: Found 1,234 results:
     
     1. WASP-12b - Run 5
        Task: transit | Algorithm: whitelight
        Instrument: JWST-NIRSpec-G395H
     
     2. GJ 436 - Run 6
        Task: transit | Algorithm: whitelight
        Instrument: JWST-NIRSpec-G235H
     
     ... and 1,232 more results
     
     Query: [r for r in data["rows"] if "jwst" in r.get("sv","").lower() 
            and r.get("task")=="transit"]
```

## How It Works

1. **Message Detection**: Checks if your message contains query keywords
   - Query keywords: show, find, get, jwst, hst, transit, eclipse, etc.
   - If detected → runs database query
   - If not → has a conversation

2. **Database Queries**: Uses the same code generation as the query interface
   - Generates Python code from your question
   - Executes against EXCALIBUR data
   - Formats results in readable text

3. **Conversations**: Uses Ollama's llama3.2 model
   - Maintains conversation history
   - Understands context
   - Provides helpful responses

## Differences from Query Interface

| Feature | Chatbot | Query Interface |
|---------|---------|-----------------|
| Conversation | ✅ Yes | ❌ No |
| Database queries | ✅ Yes | ✅ Yes |
| Results format | Text list | HTML table |
| Shows all rows | First 10 | All rows |
| Code display | At bottom | Prominent |
| Use case | Exploration | Filtering |

## Tips

- Start with "hello" or "what can you do?" to learn more
- Use natural language: "show me", "find", "get", "list"
- Be specific: "JWST transit runs" vs just "JWST"
- Ask follow-up questions in the same chat
- Click "Clear Chat" to start fresh

## Requirements

- Python 3.8+
- Ollama with llama3.2 model installed
- Same dependencies as main query interface
