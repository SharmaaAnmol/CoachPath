import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
APP_DIR = BASE_DIR / "app"
DATA_DIR = APP_DIR / "data"

class Settings:
    PROJECT_NAME: str = "CoachPath"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI-Powered Career Intelligence & Job Application Assistant - Bharat Hackathon 2.0"
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/coachpath_local.db")
    DB_PATH: Path = BASE_DIR / "coachpath_local.db"
    
    # Supabase (optional for hosted cloud mode)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    
    # AI / LLM Keys
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini") # 'gemini', 'anthropic', 'groq', 'mock'
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    LLM_FALLBACK_TO_DEMO: bool = os.getenv("LLM_FALLBACK_TO_DEMO", "true").lower() in ("true", "1")
    
    # External APIs
    ADZUNA_APP_ID: str = os.getenv("ADZUNA_APP_ID", "")
    ADZUNA_APP_KEY: str = os.getenv("ADZUNA_APP_KEY", "")
    RAPIDAPI_KEY: str = os.getenv("RAPIDAPI_KEY", "")
    
    # Demo Default User
    DEFAULT_USER_ID: str = "00000000-0000-0000-0000-000000000001"

settings = Settings()
