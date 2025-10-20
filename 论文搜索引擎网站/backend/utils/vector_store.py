from __future__ import annotations

from typing import List, Dict, Any


class VectorStore:
    """Minimal stub vector store for optional similarity search.

    In production, replace with a real embedding index (e.g., FAISS, Chroma).
    """

    def __init__(self) -> None:
        self._available: bool = False  # Toggle to True when an index is ready

    def is_available(self) -> bool:
        return self._available

    async def similarity_search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        # Return empty list when no index is configured
        return []
