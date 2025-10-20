"""
ArXiv API客户端
用于与ArXiv API交互，获取论文数据
"""

import asyncio
import aiohttp
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

class ArxivClient:
    """ArXiv API客户端"""
    
    def __init__(self):
        self.base_url = "http://export.arxiv.org/api/query"
        self.session = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def search(
        self,
        query: str,
        max_results: int = 10,
        start: int = 0,
        sort_by: str = "relevance",
        sort_order: str = "desc"
    ) -> List[Dict[str, Any]]:
        """
        搜索ArXiv论文
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
            start: 起始位置
            sort_by: 排序字段
            sort_order: 排序顺序
            
        Returns:
            List[Dict]: 论文列表
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # 构建查询参数
            params = {
                "search_query": query,
                "start": start,
                "max_results": max_results,
                "sortBy": sort_by,
                "sortOrder": sort_order
            }
            
            logger.info(f"搜索ArXiv: {query}")
            
            async with self.session.get(self.base_url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"ArXiv API请求失败: {response.status}")
                
                xml_content = await response.text()
                papers = self._parse_xml_response(xml_content)
                
                logger.info(f"ArXiv搜索完成，返回 {len(papers)} 篇论文")
                return papers
                
        except Exception as e:
            logger.error(f"ArXiv搜索失败: {str(e)}")
            raise
        finally:
            if self.session:
                await self.session.close()
                self.session = None
    
    async def get_paper_by_id(self, arxiv_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ArXiv ID获取论文详情
        
        Args:
            arxiv_id: ArXiv论文ID
            
        Returns:
            Optional[Dict]: 论文信息
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # 构建查询参数
            params = {
                "id_list": arxiv_id,
                "max_results": 1
            }
            
            logger.info(f"获取ArXiv论文: {arxiv_id}")
            
            async with self.session.get(self.base_url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"ArXiv API请求失败: {response.status}")
                
                xml_content = await response.text()
                papers = self._parse_xml_response(xml_content)
                
                if papers:
                    logger.info(f"成功获取论文: {arxiv_id}")
                    return papers[0]
                else:
                    logger.warning(f"未找到论文: {arxiv_id}")
                    return None
                    
        except Exception as e:
            logger.error(f"获取ArXiv论文失败: {str(e)}")
            return None
        finally:
            if self.session:
                await self.session.close()
                self.session = None
    
    def _parse_xml_response(self, xml_content: str) -> List[Dict[str, Any]]:
        """
        解析ArXiv XML响应
        
        Args:
            xml_content: XML内容
            
        Returns:
            List[Dict]: 解析后的论文列表
        """
        try:
            root = ET.fromstring(xml_content)
            papers = []
            
            # 定义命名空间
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'opensearch': 'http://a9.com/-/spec/opensearch/1.1/',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            # 查找所有entry元素
            entries = root.findall('.//atom:entry', namespaces)
            
            for entry in entries:
                paper = self._parse_entry(entry, namespaces)
                if paper:
                    papers.append(paper)
            
            return papers
            
        except Exception as e:
            logger.error(f"解析ArXiv XML失败: {str(e)}")
            return []
    
    def _parse_entry(self, entry, namespaces: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        解析单个entry元素
        
        Args:
            entry: XML entry元素
            namespaces: 命名空间字典
            
        Returns:
            Optional[Dict]: 论文信息
        """
        try:
            # 提取基本信息
            title_elem = entry.find('atom:title', namespaces)
            title = title_elem.text.strip() if title_elem is not None else ""
            
            summary_elem = entry.find('atom:summary', namespaces)
            abstract = summary_elem.text.strip() if summary_elem is not None else ""
            
            published_elem = entry.find('atom:published', namespaces)
            published = published_elem.text.strip() if published_elem is not None else ""
            
            # 提取作者
            authors = []
            author_elems = entry.findall('atom:author', namespaces)
            for author_elem in author_elems:
                name_elem = author_elem.find('atom:name', namespaces)
                if name_elem is not None:
                    authors.append(name_elem.text.strip())
            
            # 提取分类
            categories = []
            category_elems = entry.findall('atom:category', namespaces)
            for category_elem in category_elems:
                term = category_elem.get('term')
                if term:
                    categories.append(term)
            
            # 提取ArXiv ID
            arxiv_id = ""
            id_elem = entry.find('atom:id', namespaces)
            if id_elem is not None:
                arxiv_id = id_elem.text.split('/')[-1]
            
            # 构建论文信息
            paper = {
                "arxiv_id": arxiv_id,
                "title": title,
                "authors": authors,
                "abstract": abstract,
                "published": published,
                "categories": categories,
                "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf" if arxiv_id else "",
                "url": f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else ""
            }
            
            return paper
            
        except Exception as e:
            logger.error(f"解析entry失败: {str(e)}")
            return None
