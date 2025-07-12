"""Core configuration settings."""
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings."""
    
    def __init__(self):
        # AI/LLM settings
        self.gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
        
        # Supabase settings
        self.supabase_url: str = os.getenv("SUPABASE_URL", "")
        self.supabase_anon_key: str = os.getenv("SUPABASE_ANON_KEY", "")
        
        # API settings
        self.api_secret_key: str = os.getenv("API_SECRET_KEY", "")
        
        # Application settings
        self.debug: bool = os.getenv("DEBUG", "True").lower() == "true"
        self.environment: str = os.getenv("ENVIRONMENT", "development")
        
        # CORS settings
        origins_env = os.getenv("ALLOWED_ORIGINS", "*")
        self.allowed_origins: List[str] = [origin.strip() for origin in origins_env.split(",")]
        
        # Rate limiting
        self.rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))


# Global settings instance
settings = Settings()
