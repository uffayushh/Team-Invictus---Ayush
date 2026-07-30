from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    grobid_url: str = "http://localhost:8070"
    chroma_path: str = "./chroma_data"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    chunk_target_tokens: int = 450
    chunk_max_tokens: int = 800

    class Config:
        env_file = ".env"

settings = Settings()