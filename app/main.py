"""ChoibenAssist FastAPI Backend - AI Microservice"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Updated import path
from app.core.config import settings
from app.api.v1.endpoints import ai
from app.services.gemini_service import GeminiService


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting ChoibenAssist AI Backend...")

    try:
        gemini_service = GeminiService(settings)
        app.state.gemini_service = gemini_service
        logger.info("Gemini service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Gemini service: {e}")
        # Don't raise - let the app start without Gemini service

    yield

    # Shutdown
    logger.info("Shutting down ChoibenAssist AI Backend...")


# Create FastAPI app
app = FastAPI(
    title="ChoibenAssist AI Backend",
    description="AI microservice for learning plan generation and analysis",
    version="1.0.0",
    docs_url="/docs" if settings.enable_docs else None,
    redoc_url="/redoc" if settings.enable_docs else None,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ai.router, prefix="/api/ai", tags=["AI"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ChoibenAssist AI Backend",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/api/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": "ChoibenAssist AI Backend",
        "environment": settings.environment,
    }
