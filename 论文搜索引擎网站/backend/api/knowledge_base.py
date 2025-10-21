"""
知识库管理API接口
负责ArXiv知识库的配置、更新和统计
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import logging

from services.arxiv_knowledge_base import ArxivKnowledgeBase

router = APIRouter()
logger = logging.getLogger(__name__)

class KnowledgeBaseStats(BaseModel):
    """知识库统计信息模型"""
    last_updated: Optional[str]
    total_papers: int
    cached_papers: int
    categories: Dict[str, Any]

class KnowledgeBaseUpdateRequest(BaseModel):
    """知识库更新请求模型"""
    categories: Optional[List[str]] = None
    force_update: bool = False

class KnowledgeBaseUpdateResponse(BaseModel):
    """知识库更新响应模型"""
    success: bool
    message: str
    task_id: Optional[str] = None

class KnowledgeBaseSearchRequest(BaseModel):
    """知识库搜索请求模型"""
    query: str
    max_results: Optional[int] = 10
    categories: Optional[List[str]] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None

class KnowledgeBaseSearchResponse(BaseModel):
    """知识库搜索响应模型"""
    papers: List[Dict[str, Any]]
    total: int
    query: str
    took: float

# 全局知识库实例
knowledge_base = ArxivKnowledgeBase()

@router.get("/stats", response_model=KnowledgeBaseStats)
async def get_knowledge_base_stats():
    """
    获取知识库统计信息
    
    Returns:
        KnowledgeBaseStats: 知识库统计信息
    """
    try:
        logger.info("获取知识库统计信息")
        
        stats = knowledge_base.get_knowledge_stats()
        
        return KnowledgeBaseStats(**stats)
        
    except Exception as e:
        logger.error(f"获取知识库统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取知识库统计失败: {str(e)}")

@router.post("/update", response_model=KnowledgeBaseUpdateResponse)
async def update_knowledge_base(
    request: KnowledgeBaseUpdateRequest,
    background_tasks: BackgroundTasks
):
    """
    更新知识库
    
    Args:
        request: 更新请求参数
        background_tasks: 后台任务管理器
        
    Returns:
        KnowledgeBaseUpdateResponse: 更新结果
    """
    try:
        logger.info(f"收到知识库更新请求: {request.categories}")
        
        # 在后台执行更新任务
        background_tasks.add_task(
            knowledge_base.update_knowledge_base,
            categories=request.categories
        )
        
        return KnowledgeBaseUpdateResponse(
            success=True,
            message="知识库更新任务已启动，将在后台执行",
            task_id="update_task_001"
        )
        
    except Exception as e:
        logger.error(f"启动知识库更新失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启动知识库更新失败: {str(e)}")

@router.post("/search", response_model=KnowledgeBaseSearchResponse)
async def search_knowledge_base(request: KnowledgeBaseSearchRequest):
    """
    搜索知识库
    
    Args:
        request: 搜索请求参数
        
    Returns:
        KnowledgeBaseSearchResponse: 搜索结果
    """
    try:
        logger.info(f"知识库搜索: {request.query}")
        
        # 执行知识库搜索
        papers = await knowledge_base.search_papers(
            query=request.query,
            max_results=request.max_results,
            categories=request.categories,
            year_from=request.year_from,
            year_to=request.year_to
        )
        
        return KnowledgeBaseSearchResponse(
            papers=papers,
            total=len(papers),
            query=request.query,
            took=0.0  # 实际耗时需要在服务中计算
        )
        
    except Exception as e:
        logger.error(f"知识库搜索失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"知识库搜索失败: {str(e)}")

@router.get("/paper/{arxiv_id}")
async def get_paper_from_knowledge_base(arxiv_id: str):
    """
    从知识库获取论文详情
    
    Args:
        arxiv_id: ArXiv论文ID
        
    Returns:
        Dict: 论文详情
    """
    try:
        logger.info(f"获取论文详情: {arxiv_id}")
        
        paper = await knowledge_base.get_paper_by_id(arxiv_id)
        
        if not paper:
            raise HTTPException(status_code=404, detail=f"论文 {arxiv_id} 未找到")
        
        return {"paper": paper}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取论文详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取论文详情失败: {str(e)}")

@router.get("/categories/{category}/papers")
async def get_papers_by_category(
    category: str,
    max_results: int = 20,
    days: int = 30
):
    """
    获取指定分类的最新论文
    
    Args:
        category: 论文分类
        max_results: 最大结果数
        days: 最近多少天内的论文
        
    Returns:
        Dict: 论文列表
    """
    try:
        logger.info(f"获取分类论文: {category}")
        
        papers = await knowledge_base.get_papers_by_category(
            category=category,
            max_results=max_results,
            days=days
        )
        
        return {
            "category": category,
            "papers": papers,
            "total": len(papers)
        }
        
    except Exception as e:
        logger.error(f"获取分类论文失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取分类论文失败: {str(e)}")

@router.get("/trending")
async def get_trending_papers(days: int = 7):
    """
    获取热门论文
    
    Args:
        days: 最近多少天内的论文
        
    Returns:
        Dict: 热门论文列表
    """
    try:
        logger.info("获取热门论文")
        
        papers = await knowledge_base.get_trending_papers(days=days)
        
        return {
            "trending_papers": papers,
            "total": len(papers),
            "days": days
        }
        
    except Exception as e:
        logger.error(f"获取热门论文失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取热门论文失败: {str(e)}")

@router.get("/categories")
async def get_supported_categories():
    """
    获取支持的论文分类列表
    
    Returns:
        Dict: 分类列表
    """
    try:
        logger.info("获取支持的分类列表")
        
        categories = [
            {"id": "cs.AI", "name": "人工智能", "description": "人工智能相关研究"},
            {"id": "cs.CV", "name": "计算机视觉", "description": "计算机视觉和图像处理"},
            {"id": "cs.CL", "name": "计算语言学", "description": "自然语言处理和计算语言学"},
            {"id": "cs.LG", "name": "机器学习", "description": "机器学习理论和应用"},
            {"id": "cs.IR", "name": "信息检索", "description": "信息检索和数据挖掘"},
            {"id": "cs.NE", "name": "神经网络", "description": "神经网络和深度学习"},
            {"id": "stat.ML", "name": "统计机器学习", "description": "统计机器学习方法"},
            {"id": "cs.RO", "name": "机器人学", "description": "机器人技术和自动化"},
            {"id": "cs.CC", "name": "计算复杂性", "description": "计算复杂性和算法"},
            {"id": "cs.DS", "name": "数据结构", "description": "数据结构和算法"},
            {"id": "cs.SE", "name": "软件工程", "description": "软件工程和开发"},
            {"id": "cs.PL", "name": "编程语言", "description": "编程语言和编译器"},
            {"id": "cs.DB", "name": "数据库", "description": "数据库系统和数据管理"},
            {"id": "cs.CR", "name": "密码学", "description": "密码学和信息安全"},
            {"id": "cs.DC", "name": "分布式计算", "description": "分布式和并行计算"}
        ]
        
        return {"categories": categories}
        
    except Exception as e:
        logger.error(f"获取分类列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取分类列表失败: {str(e)}")

@router.post("/sync")
async def sync_knowledge_base():
    """
    手动同步知识库
    
    Returns:
        Dict: 同步结果
    """
    try:
        logger.info("手动同步知识库")
        
        # 执行知识库更新
        await knowledge_base.update_knowledge_base()
        
        return {
            "success": True,
            "message": "知识库同步完成",
            "stats": knowledge_base.get_knowledge_stats()
        }
        
    except Exception as e:
        logger.error(f"知识库同步失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"知识库同步失败: {str(e)}")