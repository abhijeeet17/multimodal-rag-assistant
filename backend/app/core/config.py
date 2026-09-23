import os
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[".env", "../.env"],
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "Multimodal Document Intelligence & RAG Assistant"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "sqlite:///./data/rag_assistant.db"

    # Storage
    UPLOAD_DIR: str = "./data/uploads"
    MAX_UPLOAD_SIZE_MB: int = 20
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "png", "jpg", "jpeg", "docx"]

    # ChromaDB Vector DB
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_data"
    CHROMA_COLLECTION_NAME: str = "multimodal_rag_chunks"

    # AI / Model Settings
    LLM_PROVIDER: str = "openai"  # "openai" or "mock"
    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"
    VISION_MODEL: str = "gpt-4o-mini"

    # Embeddings
    EMBEDDING_PROVIDER: str = "huggingface"  # "openai" or "huggingface"
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"

    # OCR
    TESSERACT_CMD: str = "tesseract"
    ENABLE_OCR: bool = True

    # RAG Tuning
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 100
    RETRIEVAL_TOP_K: int = 5

    def create_directories(self) -> None:
        """Ensure runtime directories exist."""
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        os.makedirs(self.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
        os.makedirs(os.path.dirname(self.DATABASE_URL.replace("sqlite:///", "")), exist_ok=True)


settings = Settings()
settings.create_directories()
