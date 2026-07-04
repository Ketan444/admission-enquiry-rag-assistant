import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file at project root
load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Admission Enquiry Assistant"
    API_V1_STR: str = "/api/v1"
    
    # Database
    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", "database/school_erp.db")
    
    # RAG Vector Database
    CHROMA_DB_DIR: str = os.getenv("CHROMA_DB_DIR", "chroma_db")
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
    
    # Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    
    # Chunking Config
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # Security / Config
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        case_sensitive = True

settings = Settings()
