"""ChoibenAssist FastAPI Backend - AI Microservice"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Updated import path
from app.core.config import settings
# Comment out imports that require additional packages for now
# from app.routers import ai, health
# from app.services.gemini_service import GeminiService


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting ChoibenAssist AI Backend...")
    
    # Initialize services later when packages are installed
    # try:
    #     gemini_service = GeminiService()
    #     app.state.gemini_service = gemini_service
    #     logger.info("Gemini service initialized successfully")
    # except Exception as e:
    #     logger.error(f"Failed to initialize Gemini service: {e}")
    #     raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down ChoibenAssist AI Backend...")


# Create FastAPI app
app = FastAPI(
    title="ChoibenAssist AI Backend",
    description="AI microservice for learning plan generation and analysis",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Include routers (will add later)
# app.include_router(health.router, prefix="/api", tags=["Health"])
# app.include_router(ai.router, prefix="/api/ai", tags=["AI"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ChoibenAssist AI Backend", 
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": "ChoibenAssist AI Backend",
        "environment": settings.environment
    }
