from fastapi import HTTPException, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict
import time
from collections import defaultdict
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Rate limiting storage (in production, use Redis)
rate_limit_storage: Dict[str, list] = defaultdict(list)

security = HTTPBearer()


async def get_api_key(authorization: Optional[str] = Header(None)) -> str:
    """Validate API key from Authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    api_key = authorization.replace("Bearer ", "")
    
    # In production, validate against database or secure storage
    if api_key != settings.api_secret_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return api_key


async def rate_limit(request: Request) -> None:
    """Rate limiting middleware"""
    client_ip = request.client.host if request.client is not None else "unknown"
    current_time = time.time()
    
    # Clean old entries (older than 1 minute)
    cutoff_time = current_time - 60
    rate_limit_storage[client_ip] = [
        timestamp for timestamp in rate_limit_storage[client_ip] 
        if timestamp > cutoff_time
    ]
    
    # Check if rate limit exceeded
    if len(rate_limit_storage[client_ip]) >= settings.rate_limit_per_minute:
        raise HTTPException(
            status_code=429, 
            detail=f"Rate limit exceeded. Maximum {settings.rate_limit_per_minute} requests per minute."
        )
    
    # Add current request timestamp
    rate_limit_storage[client_ip].append(current_time)


async def get_current_user(authorization: str = Header(None)) -> Optional[str]:
    """Get current user from authorization (for future JWT implementation)"""
    # For now, return None as we're using API key authentication
    # In the future, this could decode JWT tokens to get user info
    return None
