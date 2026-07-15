# ESP-AI REST API Documentation

Secure HTTPS API for natural language queries to the EXCALIBUR exoplanet pipeline.

## Base URL

**Testing:**
```
https://mentor0.jpl.nasa.gov:10443/api
```

**Production (after Docker deployment):**
```
https://excalibur.jpl.nasa.gov/api
```

## Authentication

*To be implemented based on JPL requirements*

## Endpoints

### 1. Health Check

Check if the API is running and data is loaded.

**Endpoint:** `GET /api/health`

**Response:**
```json
{
  "status": "healthy",
  "data_loaded": true,
  "total_runs": 14103090
}
```

---

### 2. Chat

Conversational interface for querying EXCALIBUR data.

**Endpoint:** `POST /api/chat`

**Request Body:**
```json
{
  "message": "Show me all JWST transit observations",
  "history": [
    ["Hello", "Hi! How can I help you?"],
    ["What can you do?", "I can help you query EXCALIBUR data..."]
  ]
}
```

**Response (Success):**
```json
{
  "status": "success",
  "response": "Found 946 results:\n\n1. **WASP-12** - Run 12345\n   Task: transit | Algorithm: whitelight\n   Instrument: JWST-NIRSPEC-NRS-F290LP-G395H\n\n..."
}
```

**Response (Error):**
```json
{
  "status": "error",
  "response": "",
  "error": "Model 'llama3.2' not found"
}
```

---

### 3. Query

Direct database query with natural language.

**Endpoint:** `POST /api/query`

**Request Body:**
```json
{
  "query": "All JWST transit observations"
}
```

**Response (Success):**
```json
{
  "status": "success",
  "code": "[r for r in data['rows'] if 'jwst' in r.get('sv','').lower() and r.get('task')=='transit']",
  "results": [
    {
      "run_id": 12345,
      "target": "WASP-12",
      "task": "transit",
      "alg": "whitelight",
      "sv": "JWST-NIRSPEC-NRS-F290LP-G395H"
    },
    ...
  ],
  "total": 946
}
```

**Response (Error):**
```json
{
  "status": "error",
  "error": "Generated code contains unsafe operations"
}
```

---

## Error Codes

| Status Code | Meaning |
|-------------|---------|
| 200 | Success |
| 400 | Bad Request (invalid JSON or missing fields) |
| 500 | Internal Server Error |

## Example Usage

### cURL

```bash
# Health check
curl https://mentor0.jpl.nasa.gov:10443/api/health

# Chat request
curl -X POST https://mentor0.jpl.nasa.gov:10443/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me all JWST data",
    "history": []
  }'

# Query request
curl -X POST https://mentor0.jpl.nasa.gov:10443/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "All transit observations for GJ 436"
  }'
```

### JavaScript (for Gael's frontend)

```javascript
// Chat request
async function sendChatMessage(message, history) {
  const response = await fetch('https://mentor0.jpl.nasa.gov:10443/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: message,
      history: history
    })
  });
  
  const data = await response.json();
  
  if (data.status === 'success') {
    return data.response;
  } else {
    throw new Error(data.error);
  }
}

// Query request
async function sendQuery(query) {
  const response = await fetch('https://mentor0.jpl.nasa.gov:10443/api/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query
    })
  });
  
  const data = await response.json();
  
  if (data.status === 'success') {
    return {
      code: data.code,
      results: data.results,
      total: data.total
    };
  } else {
    throw new Error(data.error);
  }
}
```

### Python

```python
import requests

# Chat request
response = requests.post(
    'https://mentor0.jpl.nasa.gov:10443/api/chat',
    json={
        'message': 'Show me all JWST data',
        'history': []
    }
)
data = response.json()
print(data['response'])

# Query request
response = requests.post(
    'https://mentor0.jpl.nasa.gov:10443/api/query',
    json={
        'query': 'All transit observations'
    }
)
data = response.json()
print(f"Found {data['total']} results")
```

## Development

### Running Locally (HTTP)

```bash
# Install dependencies
pip install fastapi uvicorn

# Run server
python api/server.py
```

Access at: `http://localhost:8000`

### Running with HTTPS

```bash
# Generate self-signed certificate (for testing)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Update server.py with certificate paths
# Run server
python api/server.py
```

Access at: `https://localhost:10443`

### API Documentation

FastAPI automatically generates interactive API documentation:
- Swagger UI: `https://mentor0.jpl.nasa.gov:10443/docs`
- ReDoc: `https://mentor0.jpl.nasa.gov:10443/redoc`

## Security

- All endpoints use HTTPS
- CORS restricted to `https://excalibur.jpl.nasa.gov`
- Input validation via Pydantic models
- Request/response logging for audit trail
- Generated code safety validation

## Deployment

See `docs/DEPLOYMENT.md` (to be created after testing)

## Support

For issues or questions, contact:
- Elizabeth Nguyen (elizabeth.s.nguyen@jpl.nasa.gov)
- Al Niessner (albert.f.niessner@jpl.nasa.gov)
