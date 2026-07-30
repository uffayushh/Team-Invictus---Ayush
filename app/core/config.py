from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/postgres"

    # --- File storage ---
    UPLOAD_DIR: str = "./uploads"

    # --- Parsing ---
    
    GROBID_BASE_URL: str = ""

    # --- Embeddings / vector store ---
    CHROMA_PERSIST_DIR: str = "./chroma_data"
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"

    # --- Chunking ---
    CHUNK_TARGET_TOKENS: int = 450
    CHUNK_MAX_TOKENS: int = 800

    # --- CORS ---
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"


settings = Settings()