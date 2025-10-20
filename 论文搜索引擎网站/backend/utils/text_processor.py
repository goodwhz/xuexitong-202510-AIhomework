from __future__ import annotations


class TextProcessor:
    """Simple text preprocessing utilities for queries and text fields."""

    def preprocess_query(self, query: str) -> str:
        if not isinstance(query, str):
            return ""
        # Basic normalization; extend as needed
        normalized = query.strip()
        return " ".join(normalized.split())
