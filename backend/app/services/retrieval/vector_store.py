import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings


class ChromaVectorStore:
    def __init__(self):
        settings.create_directories()
        self.persist_directory = os.path.abspath(settings.CHROMA_PERSIST_DIRECTORY)
        self.collection_name = settings.CHROMA_COLLECTION_NAME

        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=ChromaSettings(allow_reset=True, anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(
        self,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ) -> List[str]:
        """Insert chunks and embeddings into ChromaDB collection."""
        if not chunks or not embeddings:
            return []

        ids = [chunk["chunk_id"] for chunk in chunks]
        documents = [chunk["content"] for chunk in chunks]
        metadatas = []

        for chunk in chunks:
            meta = {
                "document_id": chunk["document_id"],
                "filename": chunk["filename"],
                "page_number": int(chunk["page_number"]),
                "chunk_id": chunk["chunk_id"],
                "content_type": str(chunk["content_type"]),
                "chunk_index": int(chunk["chunk_index"])
            }
            metadatas.append(meta)

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

        return ids

    def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = settings.RETRIEVAL_TOP_K,
        document_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search in ChromaDB.
        Returns list of matched chunks with metadata and distance.
        """
        where_clause = None
        if document_ids:
            if len(document_ids) == 1:
                where_clause = {"document_id": document_ids[0]}
            else:
                where_clause = {"document_id": {"$in": document_ids}}

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, max(1, self.collection.count())),
            where=where_clause,
            include=["documents", "metadatas", "distances"]
        )

        matched_chunks = []
        if results and results.get("ids") and len(results["ids"][0]) > 0:
            ids = results["ids"][0]
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            dists = results["distances"][0] if "distances" in results else [0.0] * len(ids)

            for i in range(len(ids)):
                matched_chunks.append({
                    "chunk_id": ids[i],
                    "content": docs[i],
                    "metadata": metas[i],
                    "distance": dists[i],
                    "document_id": metas[i].get("document_id"),
                    "filename": metas[i].get("filename"),
                    "page_number": metas[i].get("page_number", 1),
                    "content_type": metas[i].get("content_type", "text")
                })

        return matched_chunks

    def delete_document_chunks(self, document_id: str) -> None:
        """Remove all indexed chunks belonging to a document."""
        try:
            self.collection.delete(where={"document_id": document_id})
        except Exception:
            pass
