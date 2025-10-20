"""
问答相关API接口
基于RAG技术的智能问答系统
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
import logging

from services.qa_service import QAService

router = APIRouter()
logger = logging.getLogger(__name__)

class QARequest(BaseModel):
    """问答请求模型"""
    question: str
    paper_id: Optional[str] = None
    context_limit: Optional[int] = 5
    include_sources: Optional[bool] = True

class QAResponse(BaseModel):
    """问答响应模型"""
    answer: str
    sources: List[dict]
    confidence: float
    question: str
    took: float

class QASource(BaseModel):
    """问答来源模型"""
    paper_id: str
    title: str
    relevance_score: float
    snippet: str
    page_number: Optional[int] = None

@router.post("/", response_model=QAResponse)
async def ask_question(request: QARequest):
    """
    智能问答接口
    
    Args:
        request: 问答请求参数
        
    Returns:
        QAResponse: 问答结果
    """
    try:
        logger.info(f"收到问答请求: {request.question}")
        
        # 创建问答服务实例
        qa_service = QAService()
        
        # 执行问答
        result = await qa_service.ask_question(
            question=request.question,
            paper_id=request.paper_id,
            context_limit=request.context_limit,
            include_sources=request.include_sources
        )
        
        logger.info(f"问答完成，置信度: {result['confidence']}")
        
        return QAResponse(**result)
        
    except Exception as e:
        logger.error(f"问答失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"问答失败: {str(e)}")

@router.get("/suggestions")
async def get_qa_suggestions(q: str = Query(..., min_length=1)):
    """
    获取问答建议
    
    Args:
        q: 问题关键词
        
    Returns:
        List[str]: 问答建议列表
    """
    try:
        qa_service = QAService()
        suggestions = await qa_service.get_qa_suggestions(q)
        
        return {"suggestions": suggestions}
        
    except Exception as e:
        logger.error(f"获取问答建议失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取问答建议失败: {str(e)}")

@router.get("/history")
async def get_qa_history(limit: int = Query(10, ge=1, le=100)):
    """
    获取问答历史
    
    Args:
        limit: 返回数量限制
        
    Returns:
        List[dict]: 问答历史列表
    """
    try:
        qa_service = QAService()
        history = await qa_service.get_qa_history(limit)
        
        return {"history": history}
        
    except Exception as e:
        logger.error(f"获取问答历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取问答历史失败: {str(e)}")

@router.post("/feedback")
async def submit_feedback(
    question: str,
    answer: str,
    rating: int = Query(..., ge=1, le=5),
    feedback: Optional[str] = None
):
    """
    提交问答反馈
    
    Args:
        question: 问题
        answer: 回答
        rating: 评分 (1-5)
        feedback: 反馈内容
        
    Returns:
        dict: 操作结果
    """
    try:
        logger.info(f"收到反馈: 评分={rating}")
        
        qa_service = QAService()
        result = await qa_service.submit_feedback(
            question=question,
            answer=answer,
            rating=rating,
            feedback=feedback
        )
        
        return {"success": result, "message": "反馈提交成功" if result else "反馈提交失败"}
        
    except Exception as e:
        logger.error(f"提交反馈失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"提交反馈失败: {str(e)}")

@router.get("/popular")
async def get_popular_questions(limit: int = Query(10, ge=1, le=50)):
    """
    获取热门问题
    
    Args:
        limit: 返回数量限制
        
    Returns:
        List[dict]: 热门问题列表
    """
    try:
        qa_service = QAService()
        popular = await qa_service.get_popular_questions(limit)
        
        return {"popular_questions": popular}
        
    except Exception as e:
        logger.error(f"获取热门问题失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取热门问题失败: {str(e)}")

@router.get("/related")
async def get_related_questions(question: str = Query(..., min_length=1)):
    """
    获取相关问题
    
    Args:
        question: 问题文本
        
    Returns:
        List[dict]: 相关问题列表
    """
    try:
        qa_service = QAService()
        related = await qa_service.get_related_questions(question)
        
        return {"related_questions": related}
        
    except Exception as e:
        logger.error(f"获取相关问题失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取相关问题失败: {str(e)}")
