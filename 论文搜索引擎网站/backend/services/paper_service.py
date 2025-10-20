from __future__ import annotations

from typing import Optional, List, Dict, Any

from utils.arxiv_client import ArxivClient


class PaperService:
    """Service for fetching paper details and simple actions.

    This minimal version delegates metadata retrieval to ArxivClient.
    """

    def __init__(self) -> None:
        self._client = ArxivClient()

    async def get_paper_details(self, paper_id: str) -> Optional[Dict[str, Any]]:
        # paper_id corresponds to arXiv id in this project
        return await self._client.get_paper_by_id(paper_id)

    async def download_paper(self, paper_id: str, fmt: str = "pdf") -> Optional[str]:
        # For demo purposes, return direct arXiv PDF URL for pdf, otherwise None
        if fmt.lower() == "pdf":
            return f"https://arxiv.org/pdf/{paper_id}.pdf"
        return None

    async def get_paper_abstract(self, paper_id: str) -> Optional[Dict[str, Any]]:
        paper = await self._client.get_paper_by_id(paper_id)
        if not paper:
            return None
        return {"id": paper_id, "abstract": paper.get("abstract", "")}

    async def get_paper_references(self, paper_id: str) -> List[Dict[str, Any]]:
        # arXiv API does not expose references directly; return empty for now
        return []

    async def get_paper_citations(self, paper_id: str) -> Dict[str, Any]:
        # Placeholder citation info
        return {"id": paper_id, "citation_count": 0}

    async def bookmark_paper(self, paper_id: str) -> bool:
        # No persistence layer; emulate success
        return True

    async def unbookmark_paper(self, paper_id: str) -> bool:
        # No persistence layer; emulate success
        return True
