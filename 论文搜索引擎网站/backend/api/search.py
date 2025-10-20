"""
搜索相关API接口
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from pydantic import BaseModel
import logging

from services.search_service import SearchService

router = APIRouter()
logger = logging.getLogger(__name__)

class SearchRequest(BaseModel):
    """搜索请求模型"""
    query: str
    limit: Optional[int] = 10
    offset: Optional[int] = 0
    category: Optional[str] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None

class PaperInfo(BaseModel):
    """论文信息模型"""
    id: str
    title: str
    authors: List[str]
    abstract: str
    published: str
    categories: List[str]
    pdf_url: Optional[str] = None
    arxiv_id: str

class SearchResponse(BaseModel):
    """搜索响应模型"""
    papers: List[PaperInfo]
    total: int
    query: str
    took: float

@router.post("/", response_model=SearchResponse)
async def search_papers(request: SearchRequest):
    """
    搜索论文
    
    Args:
        request: 搜索请求参数
        
    Returns:
        SearchResponse: 搜索结果
    """
    try:
        logger.info(f"收到搜索请求: {request.query}")
        
        # 创建搜索服务实例
        search_service = SearchService()
        
        # 执行搜索
        results = await search_service.search_papers(
            query=request.query,
            limit=request.limit,
            offset=request.offset,
            category=request.category,
            year_from=request.year_from,
            year_to=request.year_to
        )
        
        logger.info(f"搜索完成，返回 {len(results['papers'])} 篇论文")
        
        return SearchResponse(**results)
        
    except Exception as e:
        logger.error(f"搜索失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")

@router.get("/suggestions")
async def get_search_suggestions(q: str = Query(..., min_length=1)):
    """
    获取搜索建议
    
    Args:
        q: 搜索关键词
        
    Returns:
        List[str]: 搜索建议列表
    """
    try:
        search_service = SearchService()
        suggestions = await search_service.get_search_suggestions(q)
        
        return {"suggestions": suggestions}
        
    except Exception as e:
        logger.error(f"获取搜索建议失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取搜索建议失败: {str(e)}")

@router.get("/trending")
async def get_trending_topics():
    """
    获取热门话题
    
    Returns:
        List[dict]: 热门话题列表
    """
    try:
        search_service = SearchService()
        trending = await search_service.get_trending_topics()
        
        return {"trending": trending}
        
    except Exception as e:
        logger.error(f"获取热门话题失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取热门话题失败: {str(e)}")

@router.get("/categories")
async def get_categories():
    """
    获取论文分类列表
    
    Returns:
        List[dict]: 分类列表
    """
    try:
        search_service = SearchService()
        categories = await search_service.get_categories()
        
        return {"categories": categories}
        
    except Exception as e:
        logger.error(f"获取分类失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取分类失败: {str(e)}")
