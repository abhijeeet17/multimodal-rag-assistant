from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.services.embeddings.embedding_service import EmbeddingService
from app.services.retrieval.vector_store import ChromaVectorStore


class RAGRetriever:
    def __init__(self, embedding_service: EmbeddingService = None, vector_store: ChromaVectorStore = None):
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store or ChromaVectorStore()

    def retrieve_relevant_chunks(
        self,
        query: str,
        top_k: int = settings.RETRIEVAL_TOP_K,
        document_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Embed question -> Search ChromaDB -> Return top-K relevant chunks with citations metadata.
        """
        if not query.strip():
            return []

        query_vector = self.embedding_service.embed_query(query)
        relevant_chunks = self.vector_store.similarity_search(
            query_embedding=query_vector,
            top_k=top_k,
            document_ids=document_ids
        )
        return relevant_chunks
