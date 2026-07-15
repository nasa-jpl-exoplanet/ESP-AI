"""
ESP-AI REST API Server
Provides HTTPS endpoints for chatbot and query functionality
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import logging

# Import ESP-AI components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.query_translator import generate_code, execute_query
from data.load_excalibur_data import load_excalibur_data
from ui.chatbot_interface import chat_with_excalibur

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ESP-AI API",
    description="Natural Language Interface for EXCALIBUR Exoplanet Pipeline",
    version="1.0.0"
)

# CORS configuration for Gael's frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://excalibur.jpl.nasa.gov"],  # Gael's Merlin page
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load EXCALIBUR data at startup
logger.info("Loading EXCALIBUR data...")
# Default to current directory, or use environment variable
EXCALIBUR_DATA_PATH = os.getenv("EXCALIBUR_DATA_PATH", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
logger.info(f"Data path: {EXCALIBUR_DATA_PATH}")
EXCALIBUR_DATA = load_excalibur_data(EXCALIBUR_DATA_PATH)
logger.info(f"✓ Loaded {len(EXCALIBUR_DATA.get('rows', []))} runs")


# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    history: Optional[List[List[str]]] = []

class ChatResponse(BaseModel):
    status: str
    response: str
    error: Optional[str] = None

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    status: str
    code: Optional[str] = None
    results: Optional[List[Dict[str, Any]]] = None
    total: Optional[int] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    data_loaded: bool
    total_runs: int


# API Endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint - API information"""
    return {
        "name": "ESP-AI API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "data_loaded": len(EXCALIBUR_DATA.get('rows', [])) > 0,
        "total_runs": len(EXCALIBUR_DATA.get('rows', []))
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint - conversational interface
    
    Accepts a message and chat history, returns AI response
    """
    try:
        logger.info(f"Chat request: {request.message[:100]}...")
        
        # Convert history format if needed
        history = request.history or []
        
        # Call chatbot logic
        response = chat_with_excalibur(request.message, history)
        
        logger.info(f"Chat response: {len(response)} chars")
        
        return {
            "status": "success",
            "response": response
        }
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return {
            "status": "error",
            "response": "",
            "error": str(e)
        }

@app.post("/api/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Query endpoint - direct database queries
    
    Accepts natural language query, returns results
    """
    try:
        logger.info(f"Query request: {request.query}")
        
        # Generate Python code from natural language
        code = generate_code(request.query)
        logger.info(f"Generated code: {code}")
        
        # Execute query
        results = execute_query(code, EXCALIBUR_DATA)
        
        # Ensure results is a list
        if not isinstance(results, list):
            results = [results] if results is not None else []
        
        total = len(results)
        logger.info(f"Query results: {total} rows")
        
        # Limit results to prevent huge responses
        limited_results = results[:1000]
        
        return {
            "status": "success",
            "code": code,
            "results": limited_results,
            "total": total
        }
    
    except Exception as e:
        logger.error(f"Query error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "status": "error",
        "error": exc.detail
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return {
        "status": "error",
        "error": "Internal server error"
    }


if __name__ == "__main__":
    import uvicorn
    
    # Configuration from environment variables (following ESP pattern)
    port = int(os.getenv("ESP_AI_PORT", "10443"))
    ssl_keyfile = os.getenv("ESP_AI_SSL_KEY", "/etc/ssl/server.key")
    ssl_certfile = os.getenv("ESP_AI_SSL_CERT", "/etc/ssl/server.pem")
    
    # Check if running in development mode (no SSL)
    dev_mode = os.getenv("ESP_AI_DEV_MODE", "false").lower() == "true"
    
    if dev_mode:
        # Development mode (HTTP only)
        logger.info("Running in DEVELOPMENT mode (HTTP)")
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    else:
        # Production/Testing mode (HTTPS)
        # Port must be > 10000 during testing (Al's requirement)
        # Will move to port 443 after Docker containerization
        logger.info(f"Running in PRODUCTION mode (HTTPS) on port {port}")
        logger.info(f"SSL cert: {ssl_certfile}, key: {ssl_keyfile}")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
            log_level="info"
        )
