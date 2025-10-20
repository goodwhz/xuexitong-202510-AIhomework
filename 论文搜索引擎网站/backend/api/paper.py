"""
论文相关API接口
"""

from fastapi import APIRouter, HTTPException, Query, Path
from fastapi.responses import FileResponse, StreamingResponse
from typing import Optional
import logging
import os
import io

from services.paper_service import PaperService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/{paper_id}")
async def get_paper_details(paper_id: str):
    """
    获取论文详细信息
    
    Args:
        paper_id: 论文ID
        
    Returns:
        dict: 论文详细信息
    """
    try:
        logger.info(f"获取论文详情: {paper_id}")
        
        paper_service = PaperService()
        paper_details = await paper_service.get_paper_details(paper_id)
        
        if not paper_details:
            raise HTTPException(status_code=404, detail="论文不存在")
        
        return paper_details
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取论文详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取论文详情失败: {str(e)}")

@router.get("/{paper_id}/download")
async def download_paper(paper_id: str, format: str = "pdf"):
    """
    下载论文
    
    Args:
        paper_id: 论文ID
        format: 下载格式 (pdf, txt, html)
        
    Returns:
        FileResponse: 论文文件
    """
    try:
        logger.info(f"下载论文: {paper_id}, 格式: {format}")
        
        paper_service = PaperService()
        file_path = await paper_service.download_paper(paper_id, format)
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="论文文件不存在")
        
        # 根据格式设置媒体类型
        media_types = {
            "pdf": "application/pdf",
            "txt": "text/plain",
            "html": "text/html"
        }
        
        media_type = media_types.get(format, "application/octet-stream")
        
        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=f"{paper_id}.{format}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载论文失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"下载论文失败: {str(e)}")

@router.get("/{paper_id}/abstract")
async def get_paper_abstract(paper_id: str):
    """
    获取论文摘要
    
    Args:
        paper_id: 论文ID
        
    Returns:
        dict: 论文摘要信息
    """
    try:
        logger.info(f"获取论文摘要: {paper_id}")
        
        paper_service = PaperService()
        abstract = await paper_service.get_paper_abstract(paper_id)
        
        if not abstract:
            raise HTTPException(status_code=404, detail="论文摘要不存在")
        
        return abstract
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取论文摘要失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取论文摘要失败: {str(e)}")

@router.get("/{paper_id}/references")
async def get_paper_references(paper_id: str):
    """
    获取论文参考文献
    
    Args:
        paper_id: 论文ID
        
    Returns:
        List[dict]: 参考文献列表
    """
    try:
        logger.info(f"获取论文参考文献: {paper_id}")
        
        paper_service = PaperService()
        references = await paper_service.get_paper_references(paper_id)
        
        return {"references": references}
        
    except Exception as e:
        logger.error(f"获取论文参考文献失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取论文参考文献失败: {str(e)}")

@router.get("/{paper_id}/citations")
async def get_paper_citations(paper_id: str):
    """
    获取论文引用信息
    
    Args:
        paper_id: 论文ID
        
    Returns:
        dict: 引用信息
    """
    try:
        logger.info(f"获取论文引用信息: {paper_id}")
        
        paper_service = PaperService()
        citations = await paper_service.get_paper_citations(paper_id)
        
        return citations
        
    except Exception as e:
        logger.error(f"获取论文引用信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取论文引用信息失败: {str(e)}")

@router.post("/{paper_id}/bookmark")
async def bookmark_paper(paper_id: str):
    """
    收藏论文
    
    Args:
        paper_id: 论文ID
        
    Returns:
        dict: 操作结果
    """
    try:
        logger.info(f"收藏论文: {paper_id}")
        
        paper_service = PaperService()
        result = await paper_service.bookmark_paper(paper_id)
        
        return {"success": result, "message": "收藏成功" if result else "收藏失败"}
        
    except Exception as e:
        logger.error(f"收藏论文失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"收藏论文失败: {str(e)}")

@router.delete("/{paper_id}/bookmark")
async def unbookmark_paper(paper_id: str):
    """
    取消收藏论文
    
    Args:
        paper_id: 论文ID
        
    Returns:
        dict: 操作结果
    """
    try:
        logger.info(f"取消收藏论文: {paper_id}")
        
        paper_service = PaperService()
        result = await paper_service.unbookmark_paper(paper_id)
        
        return {"success": result, "message": "取消收藏成功" if result else "取消收藏失败"}
        
    except Exception as e:
        logger.error(f"取消收藏论文失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"取消收藏论文失败: {str(e)}")
