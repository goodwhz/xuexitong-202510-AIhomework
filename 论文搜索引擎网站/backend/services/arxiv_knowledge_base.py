"""
ArXiv知识库服务
负责管理ArXiv论文作为知识库的存储、检索和更新
"""

import asyncio
import time
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

from utils.arxiv_client import ArxivClient
from utils.vector_store import VectorStore
from utils.text_processor import TextProcessor
from utils.config import config

logger = logging.getLogger(__name__)

class ArxivKnowledgeBase:
    """ArXiv知识库管理类"""
    
    def __init__(self, data_dir: str = None):
        self.arxiv_client = ArxivClient()
        self.vector_store = VectorStore()
        self.text_processor = TextProcessor()
        self.data_dir = Path(data_dir or config.KNOWLEDGE_BASE_DATA_DIR)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 知识库缓存
        self._cache_file = self.data_dir / "knowledge_cache.json"
        self._knowledge_cache = self._load_cache()
    
    def _load_cache(self) -> Dict[str, Any]:
        """加载知识库缓存"""
        if self._cache_file.exists():
            try:
                with open(self._cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载知识库缓存失败: {str(e)}")
        
        return {
            "last_updated": None,
            "total_papers": 0,
            "categories": {},
            "papers": {}
        }
    
    def _save_cache(self):
        """保存知识库缓存"""
        try:
            with open(self._cache_file, 'w', encoding='utf-8') as f:
                json.dump(self._knowledge_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存知识库缓存失败: {str(e)}")
    
    async def search_papers(
        self,
        query: str,
        max_results: int = 10,
        categories: Optional[List[str]] = None,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        搜索ArXiv论文
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
            categories: 论文分类筛选
            year_from: 起始年份
            year_to: 结束年份
            use_cache: 是否使用缓存
            
        Returns:
            List[Dict]: 论文列表
        """
        start_time = time.time()
        
        try:
            logger.info(f"知识库搜索: {query}")
            
            # 1. 预处理查询
            processed_query = self.text_processor.preprocess_query(query)
            
            # 2. 执行ArXiv搜索
            papers = await self.arxiv_client.search(
                query=processed_query,
                max_results=max_results * 2,  # 获取更多结果用于筛选
                sort_by="relevance",
                sort_order="desc"
            )
            
            # 3. 应用筛选条件
            filtered_papers = self._apply_filters(
                papers, 
                categories=categories,
                year_from=year_from,
                year_to=year_to
            )
            
            # 4. 向量相似度搜索（如果启用）
            if self.vector_store.is_available():
                vector_results = await self.vector_store.similarity_search(
                    query=processed_query,
                    limit=max_results
                )
                # 合并结果
                filtered_papers = self._merge_results(filtered_papers, vector_results)
            
            # 5. 排序和截断
            sorted_papers = self._sort_papers(filtered_papers, processed_query)
            final_results = sorted_papers[:max_results]
            
            # 6. 更新缓存
            if use_cache:
                self._update_cache(final_results)
            
            took_time = time.time() - start_time
            logger.info(f"知识库搜索完成，返回 {len(final_results)} 篇论文，耗时 {took_time:.2f}秒")
            
            return final_results
            
        except Exception as e:
            logger.error(f"知识库搜索失败: {str(e)}")
            raise
    
    async def get_paper_by_id(self, arxiv_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ArXiv ID获取论文详情
        
        Args:
            arxiv_id: ArXiv论文ID
            
        Returns:
            Optional[Dict]: 论文信息
        """
        try:
            # 先检查缓存
            if arxiv_id in self._knowledge_cache["papers"]:
                cached_paper = self._knowledge_cache["papers"][arxiv_id]
                # 检查缓存是否过期（7天）
                cache_time = datetime.fromisoformat(cached_paper["cached_at"])
                if datetime.now() - cache_time < timedelta(days=7):
                    logger.info(f"从缓存获取论文: {arxiv_id}")
                    return cached_paper
            
            # 从ArXiv API获取
            paper = await self.arxiv_client.get_paper_by_id(arxiv_id)
            
            if paper:
                # 更新缓存
                paper["cached_at"] = datetime.now().isoformat()
                self._knowledge_cache["papers"][arxiv_id] = paper
                self._save_cache()
            
            return paper
            
        except Exception as e:
            logger.error(f"获取论文详情失败: {str(e)}")
            return None
    
    async def get_papers_by_category(
        self, 
        category: str, 
        max_results: int = 20,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        获取指定分类的最新论文
        
        Args:
            category: 论文分类
            max_results: 最大结果数
            days: 最近多少天内的论文
            
        Returns:
            List[Dict]: 论文列表
        """
        try:
            # 构建查询：指定分类 + 时间范围
            date_filter = datetime.now() - timedelta(days=days)
            date_str = date_filter.strftime("%Y-%m-%d")
            
            query = f"cat:{category} AND submittedDate:[{date_str} TO NOW]"
            
            papers = await self.arxiv_client.search(
                query=query,
                max_results=max_results,
                sort_by="submittedDate",
                sort_order="desc"
            )
            
            # 更新分类统计
            self._update_category_stats(category, len(papers))
            
            return papers
            
        except Exception as e:
            logger.error(f"获取分类论文失败: {str(e)}")
            return []
    
    async def get_trending_papers(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        获取热门论文（基于引用和下载量预测）
        
        Args:
            days: 最近多少天内的论文
            
        Returns:
            List[Dict]: 热门论文列表
        """
        try:
            # 搜索热门关键词组合
            trending_queries = [
                "machine learning",
                "deep learning", 
                "artificial intelligence",
                "neural networks",
                "natural language processing"
            ]
            
            all_papers = []
            
            for query in trending_queries:
                papers = await self.arxiv_client.search(
                    query=query,
                    max_results=10,
                    sort_by="relevance",
                    sort_order="desc"
                )
                all_papers.extend(papers)
            
            # 去重和排序
            unique_papers = self._deduplicate_papers(all_papers)
            sorted_papers = self._sort_by_popularity(unique_papers)
            
            return sorted_papers[:20]  # 返回前20篇
            
        except Exception as e:
            logger.error(f"获取热门论文失败: {str(e)}")
            return []
    
    async def update_knowledge_base(self, categories: List[str] = None):
        """
        更新知识库
        
        Args:
            categories: 要更新的分类列表
        """
        if categories is None:
            categories = ["cs.AI", "cs.CV", "cs.CL", "cs.LG", "stat.ML"]
        
        try:
            logger.info(f"开始更新知识库，分类: {categories}")
            
            total_updated = 0
            
            for category in categories:
                # 获取每个分类的最新论文
                papers = await self.get_papers_by_category(category, max_results=50, days=30)
                
                # 更新向量存储
                if self.vector_store.is_available() and papers:
                    await self.vector_store.add_documents(papers)
                
                total_updated += len(papers)
                logger.info(f"分类 {category} 更新了 {len(papers)} 篇论文")
            
            # 更新缓存信息
            self._knowledge_cache["last_updated"] = datetime.now().isoformat()
            self._knowledge_cache["total_papers"] = total_updated
            self._save_cache()
            
            logger.info(f"知识库更新完成，共更新 {total_updated} 篇论文")
            
        except Exception as e:
            logger.error(f"更新知识库失败: {str(e)}")
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        return {
            "last_updated": self._knowledge_cache.get("last_updated"),
            "total_papers": self._knowledge_cache.get("total_papers", 0),
            "cached_papers": len(self._knowledge_cache.get("papers", {})),
            "categories": self._knowledge_cache.get("categories", {})
        }
    
    def _apply_filters(
        self,
        papers: List[Dict],
        categories: Optional[List[str]] = None,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None
    ) -> List[Dict]:
        """应用筛选条件"""
        filtered = papers
        
        if categories:
            filtered = [p for p in filtered if any(cat in p.get("categories", []) for cat in categories)]
        
        if year_from or year_to:
            filtered = [p for p in filtered if self._check_year_filter(p, year_from, year_to)]
        
        return filtered
    
    def _check_year_filter(self, paper: Dict, year_from: Optional[int], year_to: Optional[int]) -> bool:
        """检查年份筛选条件"""
        try:
            published = paper.get("published", "")
            if not published:
                return True
            
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
    
    def _sort_papers(self, papers: List[Dict], query: str) -> List[Dict]:
        """对论文进行排序"""
        def sort_key(paper):
            score = 0
            
            # 标题匹配度
            title = paper.get("title", "").lower()
            query_lower = query.lower()
            if query_lower in title:
                score += 10
            
            # 摘要匹配度
            abstract = paper.get("abstract", "").lower()
            query_words = query_lower.split()
            for word in query_words:
                if word in abstract:
                    score += 1
            
            # 发布时间（越新越好）
            published = paper.get("published", "")
            if published:
                try:
                    year = int(published.split("-")[0])
                    score += (year - 2000) * 0.01
                except:
                    pass
            
            return -score  # 降序排列
        
        return sorted(papers, key=sort_key)
    
    def _deduplicate_papers(self, papers: List[Dict]) -> List[Dict]:
        """论文去重"""
        seen = set()
        unique = []
        
        for paper in papers:
            arxiv_id = paper.get("arxiv_id")
            if arxiv_id and arxiv_id not in seen:
                seen.add(arxiv_id)
                unique.append(paper)
        
        return unique
    
    def _sort_by_popularity(self, papers: List[Dict]) -> List[Dict]:
        """按热度排序"""
        # 简单的热度计算：基于标题长度、摘要长度、分类数量等
        def popularity_score(paper):
            score = 0
            
            # 标题长度（适中最好）
            title_len = len(paper.get("title", ""))
            if 20 <= title_len <= 100:
                score += 1
            
            # 摘要长度
            abstract_len = len(paper.get("abstract", ""))
            if abstract_len > 500:
                score += 1
            
            # 分类数量
            categories = paper.get("categories", [])
            score += min(len(categories), 3) * 0.5
            
            # 作者数量
            authors = paper.get("authors", [])
            score += min(len(authors), 5) * 0.2
            
            return -score  # 降序排列
        
        return sorted(papers, key=popularity_score)
    
    def _update_cache(self, papers: List[Dict]):
        """更新缓存"""
        for paper in papers:
            arxiv_id = paper.get("arxiv_id")
            if arxiv_id:
                paper["cached_at"] = datetime.now().isoformat()
                self._knowledge_cache["papers"][arxiv_id] = paper
        
        self._save_cache()
    
    def _update_category_stats(self, category: str, count: int):
        """更新分类统计"""
        if "categories" not in self._knowledge_cache:
            self._knowledge_cache["categories"] = {}
        
        self._knowledge_cache["categories"][category] = count
        self._save_cache()