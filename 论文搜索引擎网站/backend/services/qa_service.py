from __future__ import annotations

import time
from typing import List, Optional, Dict, Any

import logging
from services.rag_service import answer_with_citations


logger = logging.getLogger(__name__)


class QAService:
    """Service layer for QA endpoints. Wraps RAG pipeline and stubs aux endpoints."""

    async def ask_question(
        self,
        question: str,
        paper_id: Optional[str] = None,
        context_limit: Optional[int] = 5,
        include_sources: Optional[bool] = True,
    ) -> Dict[str, Any]:
        start = time.time()
        result = await answer_with_citations(question)
        took = round(time.time() - start, 3)

        sources: List[Dict[str, Any]] = []
        if include_sources:
            for c in result.get("citations", []):
                # best-effort parse: markdown [title](url)
                if "](" in c and c.endswith(")"):
                    title = c.split("](") [0].lstrip("[")
                    url = c.split("](") [1][:-1]
                else:
                    title, url = c, ""
                sources.append({
                    "title": title,
                    "url": url,
                    "relevance_score": 0.0,
                })

        return {
            "answer": result.get("answer", ""),
            "sources": sources,
            "confidence": 0.5,  # placeholder
            "question": question,
            "took": took,
        }

    async def get_qa_suggestions(self, q: str) -> List[str]:
        return [q, f"{q} 的定义是什么？", f"{q} 的最新研究进展？"]

    async def get_qa_history(self, limit: int) -> List[Dict[str, Any]]:
        return []

    async def submit_feedback(self, question: str, answer: str, rating: int, feedback: Optional[str]) -> bool:
        logger.info(f"QA feedback rating={rating}: {feedback}")
        return True

    async def get_popular_questions(self, limit: int) -> List[Dict[str, Any]]:
        return []

    async def get_related_questions(self, question: str) -> List[Dict[str, Any]]:
        return []


