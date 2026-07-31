from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/postgres"

    
    UPLOAD_DIR: str = "./uploads"

    
    GROBID_BASE_URL: str = ""

    
    CHROMA_PERSIST_DIR: str = "./chroma_data"
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"

    
    CHUNK_TARGET_TOKENS: int = 450
    CHUNK_MAX_TOKENS: int = 800

  
    LLM_PROVIDER: str = "gemini"          # "gemini" | "groq" — flip this if one rate-limits mid-demo
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"

    
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"


settings = Settings()