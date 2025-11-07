"""
LLMSec Demo FastAPI Application
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware  # UPDATED BY CLAUDE
from contextlib import asynccontextmanager
import logging
import os

from api.routes import chat, rag, debug

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 LLMSec Demo API starting...")
    yield
    logger.info("👋 LLMSec Demo API shutting down...")


app = FastAPI(
    title="LLMSec Demo API",
    description="Vulnerable vs. Defended LLM Patterns",
    version="1.0.0",
    lifespan=lifespan
)

# UPDATED BY CLAUDE: Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include API routers
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(rag.router, prefix="/rag", tags=["rag"])
app.include_router(debug.router, prefix="/logs", tags=["debug"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "llmsec-demo"}


# Mount static frontend at root
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

    @app.get("/")
    async def serve_frontend():
        """Serve frontend index.html"""
        return FileResponse(os.path.join(frontend_path, "index.html"))
