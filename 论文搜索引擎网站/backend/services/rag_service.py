from __future__ import annotations

import re
from typing import List, Dict, Any

import logging
from utils.llm import LocalQwenLLM
from utils.arxiv_client import ArxivClient

# LangChain 0.3 style imports
from langchain_core.prompts import PromptTemplate


logger = logging.getLogger(__name__)


def _build_citation(item: Dict[str, Any]) -> str:
    title = item.get("title", "Untitled")
    pid = item.get("arxiv_id", "")
    url = item.get("pdf_url") or (f"https://arxiv.org/pdf/{pid}.pdf" if pid else "")
    return f"[{title}]({url})"


async def retrieve_context(question: str, k: int = 5) -> List[Dict[str, Any]]:
    """Simple retriever over arXiv by querying with the question text.

    For demo purposes we use arXiv search results (primarily abstracts) as the
    retrievable context. A production setup should chunk PDFs and index embeddings.
    """
    client = ArxivClient()
    papers = await client.search(query=question, max_results=k)
    return papers


def build_prompt(context_blocks: List[Dict[str, Any]], question: str) -> str:
    context_texts: List[str] = []
    for i, p in enumerate(context_blocks, start=1):
        context_texts.append(
            f"[{i}] Title: {p.get('title','')}\n"
            f"Authors: {', '.join(p.get('authors', []))}\n"
            f"Abstract: {p.get('abstract','')[:1200]}\n"
            f"URL: {p.get('pdf_url','')}\n"
        )
    context_joined = "\n---\n".join(context_texts)

    template = (
        "你是一个严谨的学术助手。基于给定的论文摘要与链接，"
        "用中文回答用户问题，并在答案末尾以[编号]的形式标注引用来源列表中的编号。"
        "若无法从给定内容得到答案，请明确说明不知道，不要编造。\n\n"
        "已检索到的论文片段：\n{context}\n\n"
        "问题：{question}\n"
        "请给出简明、准确的回答。"
    )
    prompt = PromptTemplate.from_template(template)
    return prompt.format(context=context_joined, question=question)


async def answer_with_citations(question: str) -> Dict[str, Any]:
    """Run retrieval (arXiv abstracts) + local Qwen generation with citation markers.

    Returns dict: { answer: str, citations: [str] }
    """
    contexts = await retrieve_context(question, k=5)
    if not contexts:
        return {"answer": "未找到相关论文，暂无法回答该问题。", "citations": []}

    prompt_text = build_prompt(contexts, question)
    llm = LocalQwenLLM()
    answer = llm.generate(prompt_text)

    # Map bracket numbers [1], [2] ... to citations
    indices = sorted(set(int(n) for n in re.findall(r"\[(\d+)\]", answer) if n.isdigit()))
    citations: List[str] = []
    for idx in indices:
        if 1 <= idx <= len(contexts):
            citations.append(_build_citation(contexts[idx - 1]))

    return {"answer": answer.strip(), "citations": citations}


