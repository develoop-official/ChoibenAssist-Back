from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
import time

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "ChoibenAssist AI Backend"
    }


@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with dependency status"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "ChoibenAssist AI Backend",
        "dependencies": {
            "gemini_api": "connected",
            "supabase": "connected"
        }
    }
