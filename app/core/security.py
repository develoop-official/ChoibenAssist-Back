"""Security functionality for API authentication."""

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings

# HTTPBearer security scheme
security = HTTPBearer()


def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Verify API key from Authorization header.
    
    Args:
        credentials: HTTP Authorization credentials
        
    Returns:
        str: Verified API key
        
    Raises:
        HTTPException: If API key is invalid
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if the provided token matches our API secret key
    if credentials.credentials != settings.api_secret_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return credentials.credentials


def get_current_api_key(api_key: str = Depends(verify_api_key)) -> str:
    """
    Dependency to get current verified API key.
    
    Args:
        api_key: Verified API key from verify_api_key
        
    Returns:
        str: Current API key
    """
    return api_key
