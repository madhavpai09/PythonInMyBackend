import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://miniuber_user:miniuber_pass@localhost:5432/miniuber_db")
    SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT = int(os.getenv("SERVER_PORT", 8000))
    
    # Database fallback for development
    USE_POSTGRES = os.getenv("USE_POSTGRES", "false").lower() == "true"

settings = Settings()