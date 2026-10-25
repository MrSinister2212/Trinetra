import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "TRINETRA OSINT Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "trinetra-super-secret-production-grade-osint-key-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./trinetra.db"
    
    # Tor Proxy & Verification
    TOR_SOCKS_PROXY: str = "socks5h://127.0.0.1:9050"
    TOR_CHECK_URL: str = "https://check.torproject.org/api/ip"
    
    # Search Engine APIs (Optional, gracefully fall back to open/archive)
    HIBP_API_KEY: Optional[str] = None
    GOOGLE_CSE_KEY: Optional[str] = None
    GOOGLE_CSE_CX: Optional[str] = None
    BRAVE_SEARCH_API_KEY: Optional[str] = None
    SEARXNG_URL: Optional[str] = "https://searx.be"
    
    # Rate Limiting
    RATE_LIMIT_COOLDOWN_SECONDS: int = 5
    MAX_REQUESTS_PER_MINUTE: int = 60

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
