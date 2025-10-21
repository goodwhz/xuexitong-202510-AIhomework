"""
知识库初始化脚本
用于首次启动时初始化ArXiv知识库
"""

import asyncio
import logging
import time
from pathlib import Path

# 添加项目根目录到Python路径
import sys
sys.path.append(str(Path(__file__).parent.parent))

from services.arxiv_knowledge_base import ArxivKnowledgeBase
from utils.config import config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def init_knowledge_base():
    """初始化知识库"""
    logger.info("开始初始化ArXiv知识库...")
    
    try:
        # 创建知识库实例
        knowledge_base = ArxivKnowledgeBase()
        
        # 打印配置信息
        config.print_config()
        
        # 验证配置
        if not config.validate():
            logger.error("配置验证失败，请检查环境变量设置")
            return False
        
        logger.info("配置验证通过")
        
        # 创建数据目录
        data_dir = Path(config.KNOWLEDGE_BASE_DATA_DIR)
        data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"数据目录已创建: {data_dir.absolute()}")
        
        # 初始化知识库
        start_time = time.time()
        
        logger.info("开始更新知识库内容...")
        await knowledge_base.update_knowledge_base()
        
        # 获取统计信息
        stats = knowledge_base.get_knowledge_stats()
        
        end_time = time.time()
        logger.info(f"知识库初始化完成，耗时: {end_time - start_time:.2f}秒")
        logger.info(f"知识库统计: {stats}")
        
        return True
        
    except Exception as e:
        logger.error(f"知识库初始化失败: {str(e)}")
        return False

async def test_knowledge_base():
    """测试知识库功能"""
    logger.info("开始测试知识库功能...")
    
    try:
        knowledge_base = ArxivKnowledgeBase()
        
        # 测试搜索功能
        test_queries = ["machine learning", "deep learning", "neural networks"]
        
        for query in test_queries:
            logger.info(f"测试搜索: {query}")
            papers = await knowledge_base.search_papers(query, max_results=5)
            logger.info(f"搜索 '{query}' 返回 {len(papers)} 篇论文")
            
            if papers:
                for i, paper in enumerate(papers[:3]):  # 只显示前3篇
                    logger.info(f"  {i+1}. {paper.get('title', 'N/A')}")
        
        # 测试获取论文详情
        if papers:
            test_paper_id = papers[0].get("arxiv_id")
            if test_paper_id:
                logger.info(f"测试获取论文详情: {test_paper_id}")
                paper_detail = await knowledge_base.get_paper_by_id(test_paper_id)
                if paper_detail:
                    logger.info(f"论文详情获取成功: {paper_detail.get('title', 'N/A')}")
        
        logger.info("知识库功能测试完成")
        return True
        
    except Exception as e:
        logger.error(f"知识库测试失败: {str(e)}")
        return False

async def main():
    """主函数"""
    logger.info("=== ArXiv知识库初始化脚本 ===")
    
    # 初始化知识库
    success = await init_knowledge_base()
    
    if success:
        logger.info("知识库初始化成功")
        
        # 测试知识库功能
        test_success = await test_knowledge_base()
        
        if test_success:
            logger.info("知识库功能测试通过")
            logger.info("知识库已准备就绪，可以启动服务了")
        else:
            logger.warning("知识库功能测试失败，请检查配置")
    else:
        logger.error("知识库初始化失败")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())