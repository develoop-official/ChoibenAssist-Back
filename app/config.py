from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # AI/LLM settings
    gemini_api_key: str = ""
    
    # Supabase settings
    supabase_url: str = ""
    supabase_anon_key: str = ""
    
    # API settings
    api_secret_key: str = ""
    
    # Application settings
    debug: bool = False
    environment: str = "production"
    
    # CORS settings
    allowed_origins: list[str] = ["http://localhost:3000", "https://your-frontend-domain.com"]
    
    # Rate limiting
    rate_limit_per_minute: int = 100
    
    class Config:
        env_file = ".env"


settings = Settings()
