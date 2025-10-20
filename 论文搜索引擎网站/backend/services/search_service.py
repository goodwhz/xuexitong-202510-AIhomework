"""
搜索服务
负责处理论文搜索相关的业务逻辑
"""

import asyncio
import time
from typing import List, Dict, Optional, Any
import logging
from datetime import datetime

from utils.arxiv_client import ArxivClient
from utils.vector_store import VectorStore
from utils.text_processor import TextProcessor

logger = logging.getLogger(__name__)

class SearchService:
    """搜索服务类"""
    
    def __init__(self):
        self.arxiv_client = ArxivClient()
        self.vector_store = VectorStore()
        self.text_processor = TextProcessor()
        
    async def search_papers(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
        category: Optional[str] = None,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        搜索论文
        
        Args:
            query: 搜索查询
            limit: 返回数量限制
            offset: 偏移量
            category: 论文分类
            year_from: 起始年份
            year_to: 结束年份
            
        Returns:
            Dict: 搜索结果
        """
        start_time = time.time()
        
        try:
            logger.info(f"开始搜索: {query}")
            
            # 1. 预处理查询
            processed_query = self.text_processor.preprocess_query(query)
            
            # 2. 执行ArXiv搜索
            arxiv_results = await self.arxiv_client.search(
                query=processed_query,
                max_results=limit * 2,  # 获取更多结果用于筛选
                sort_by="relevance",
                sort_order="desc"
            )
            
            # 3. 应用筛选条件
            filtered_results = self._apply_filters(
                arxiv_results,
                category=category,
                year_from=year_from,
                year_to=year_to
            )
            
            # 4. 向量相似度搜索（如果启用）
            if self.vector_store.is_available():
                vector_results = await self.vector_store.similarity_search(
                    query=processed_query,
                    limit=limit
                )
                # 合并结果
                filtered_results = self._merge_results(filtered_results, vector_results)
            
            # 5. 排序和分页
            sorted_results = self._sort_results(filtered_results, processed_query)
            paginated_results = sorted_results[offset:offset + limit]
            
            # 6. 格式化结果
            formatted_results = self._format_results(paginated_results)
            
            took_time = time.time() - start_time
            
            return {
                "papers": formatted_results,
                "total": len(sorted_results),
                "query": query,
                "took": took_time
            }
            
        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            raise
    
    async def get_search_suggestions(self, query: str) -> List[str]:
        """
        获取搜索建议
        
        Args:
            query: 查询文本
            
        Returns:
            List[str]: 建议列表
        """
        try:
            # 基于历史搜索和热门关键词生成建议
            suggestions = await self._generate_suggestions(query)
            return suggestions[:10]  # 返回前10个建议
            
        except Exception as e:
            logger.error(f"获取搜索建议失败: {str(e)}")
            return []
    
    async def get_trending_topics(self) -> List[Dict[str, Any]]:
        """
        获取热门话题
        
        Returns:
            List[Dict]: 热门话题列表
        """
        try:
            # 基于最近一周的搜索统计获取热门话题
            trending = await self._get_trending_from_stats()
            return trending
            
        except Exception as e:
            logger.error(f"获取热门话题失败: {str(e)}")
            return []
    
    async def get_categories(self) -> List[Dict[str, Any]]:
        """
        获取论文分类列表
        
        Returns:
            List[Dict]: 分类列表
        """
        try:
            categories = [
                {"id": "cs.AI", "name": "人工智能", "count": 0},
                {"id": "cs.CV", "name": "计算机视觉", "count": 0},
                {"id": "cs.CL", "name": "计算语言学", "count": 0},
                {"id": "cs.LG", "name": "机器学习", "count": 0},
                {"id": "cs.IR", "name": "信息检索", "count": 0},
                {"id": "cs.NE", "name": "神经网络", "count": 0},
                {"id": "stat.ML", "name": "统计机器学习", "count": 0},
                {"id": "cs.RO", "name": "机器人学", "count": 0},
                {"id": "cs.CC", "name": "计算复杂性", "count": 0},
                {"id": "cs.DS", "name": "数据结构", "count": 0}
            ]
            return categories
            
        except Exception as e:
            logger.error(f"获取分类失败: {str(e)}")
            return []
    
    def _apply_filters(
        self,
        results: List[Dict],
        category: Optional[str] = None,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None
    ) -> List[Dict]:
        """应用筛选条件"""
        filtered = results
        
        if category:
            filtered = [r for r in filtered if category in r.get("categories", [])]
        
        if year_from or year_to:
            filtered = [r for r in filtered if self._check_year_filter(r, year_from, year_to)]
        
        return filtered
    
    def _check_year_filter(self, result: Dict, year_from: Optional[int], year_to: Optional[int]) -> bool:
        """检查年份筛选条件"""
        try:
            published = result.get("published", "")
            if not published:
                return True
            
            # 解析日期
            year = int(published.split("-")[0])
            
            if year_from and year < year_from:
                return False
            if year_to and year > year_to:
                return False
            
            return True
        except:
            return True
    
    def _merge_results(self, arxiv_results: List[Dict], vector_results: List[Dict]) -> List[Dict]:
        """合并ArXiv和向量搜索结果"""
        # 简单的合并策略：优先向量搜索结果，然后补充ArXiv结果
        merged = []
        arxiv_ids = set()
        
        # 添加向量搜索结果
        for result in vector_results:
            arxiv_id = result.get("arxiv_id")
            if arxiv_id:
                merged.append(result)
                arxiv_ids.add(arxiv_id)
        
        # 补充ArXiv结果
        for result in arxiv_results:
            arxiv_id = result.get("arxiv_id")
            if arxiv_id and arxiv_id not in arxiv_ids:
                merged.append(result)
                arxiv_ids.add(arxiv_id)
        
        return merged
    
    def _sort_results(self, results: List[Dict], query: str) -> List[Dict]:
        """对结果进行排序"""
        # 基于相关性、引用数、发布时间等因素排序
        def sort_key(result):
            score = 0
            
            # 标题匹配度
            title = result.get("title", "").lower()
            query_lower = query.lower()
            if query_lower in title:
                score += 10
            
            # 摘要匹配度
            abstract = result.get("abstract", "").lower()
            query_words = query_lower.split()
            for word in query_words:
                if word in abstract:
                    score += 1
            
            # 引用数（如果有）
            citations = result.get("citation_count", 0)
            score += citations * 0.1
            
            # 发布时间（越新越好）
            published = result.get("published", "")
            if published:
                try:
                    year = int(published.split("-")[0])
                    score += (year - 2000) * 0.01
                except:
                    pass
            
            return -score  # 降序排列
        
        return sorted(results, key=sort_key)
    
    def _format_results(self, results: List[Dict]) -> List[Dict]:
        """格式化搜索结果"""
        formatted = []
        
        for result in results:
            formatted_result = {
                "id": result.get("arxiv_id", ""),
                "title": result.get("title", ""),
                "authors": result.get("authors", []),
                "abstract": result.get("abstract", ""),
                "published": result.get("published", ""),
                "categories": result.get("categories", []),
                "pdf_url": result.get("pdf_url", ""),
                "arxiv_id": result.get("arxiv_id", "")
            }
            formatted.append(formatted_result)
        
        return formatted
    
    async def _generate_suggestions(self, query: str) -> List[str]:
        """生成搜索建议"""
        # 这里可以实现基于历史搜索、热门关键词等的建议生成
        # 暂时返回一些示例建议
        suggestions = [
            "machine learning",
            "deep learning",
            "natural language processing",
            "computer vision",
            "neural networks",
            "artificial intelligence",
            "data mining",
            "information retrieval"
        ]
        
        # 过滤包含查询词的建议
        filtered = [s for s in suggestions if query.lower() in s.lower()]
        return filtered[:10]
    
    async def _get_trending_from_stats(self) -> List[Dict[str, Any]]:
        """从统计数据获取热门话题"""
        # 这里可以实现基于搜索统计的热门话题获取
        # 暂时返回一些示例数据
        trending = [
            {"topic": "ChatGPT", "count": 1250},
            {"topic": "GPT-4", "count": 980},
            {"topic": "Transformer", "count": 850},
            {"topic": "LLM", "count": 720},
            {"topic": "BERT", "count": 650}
        ]
        return trending
