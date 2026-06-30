from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any

from app.ai.embeddings import deterministic_embedding
from app.vectorstore.chroma_client import get_or_create_collection

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _load_model():
    try:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer("all-MiniLM-L6-v2")
    except Exception as exc:
        logger.warning("SentenceTransformer unavailable; using deterministic fallback embeddings: %s", exc)
        return None


def embed_text(text: str) -> list[float]:
    model = _load_model()
    if model is None:
        return deterministic_embedding(text)
    return model.encode(text, normalize_embeddings=True).tolist()


class EmbeddingService:
    def add_embedding(self, collection_name: str, item_id: str, text: str, metadata: dict[str, Any] | None = None) -> None:
        try:
            collection = get_or_create_collection(collection_name)
            collection.upsert(ids=[item_id], documents=[text], embeddings=[embed_text(text)], metadatas=[metadata or {}])
        except Exception as exc:
            logger.warning("Could not add embedding to %s/%s: %s", collection_name, item_id, exc)

    def search_embedding(
        self,
        collection_name: str,
        query: str,
        *,
        limit: int = 5,
        where: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        try:
            collection = get_or_create_collection(collection_name)
            return collection.query(query_embeddings=[embed_text(query)], n_results=limit, where=where)
        except Exception as exc:
            logger.warning("Could not search embeddings in %s: %s", collection_name, exc)
            return {"ids": [[]], "documents": [[]], "distances": [[]]}

    def update_embedding(self, collection_name: str, item_id: str, text: str, metadata: dict[str, Any] | None = None) -> None:
        self.add_embedding(collection_name, item_id, text, metadata)

    def delete_embedding(self, collection_name: str, item_id: str) -> None:
        try:
            collection = get_or_create_collection(collection_name)
            collection.delete(ids=[item_id])
        except Exception as exc:
            logger.warning("Could not delete embedding from %s/%s: %s", collection_name, item_id, exc)


embedding_service = EmbeddingService()
