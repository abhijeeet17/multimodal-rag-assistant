from typing import List
from app.core.config import settings


class EmbeddingService:
    def __init__(self):
        self.provider = settings.EMBEDDING_PROVIDER.lower()
        self.model_name = settings.EMBEDDING_MODEL_NAME
        self._embedder = None
        self._init_embedder()

    def _init_embedder(self):
        if self.provider == "openai" and settings.OPENAI_API_KEY:
            try:
                from langchain_openai import OpenAIEmbeddings
                self._embedder = OpenAIEmbeddings(
                    openai_api_key=settings.OPENAI_API_KEY,
                    model="text-embedding-3-small"
                )
                return
            except Exception as e:
                pass

        # Fallback to local HuggingFace Embeddings
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            self._embedder = HuggingFaceEmbeddings(
                model_name=self.model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        except Exception:
            self._embedder = None

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding vector for single text string."""
        if not text:
            return []
        if self._embedder:
            return self._embedder.embed_query(text)
        # Deterministic fallback vector for testing/mock environment
        return [0.01 * (i % 50) for i in range(384)]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embedding vectors for batch of document chunks."""
        if not texts:
            return []
        if self._embedder:
            return self._embedder.embed_documents(texts)
        return [[0.01 * ((i + idx) % 50) for i in range(384)] for idx, _ in enumerate(texts)]

    def embed_query(self, query: str) -> List[float]:
        """Generate embedding vector for user query."""
        return self.embed_text(query)
