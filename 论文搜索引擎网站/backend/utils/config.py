"""
配置管理模块
统一管理应用配置和环境变量
"""

import os
from typing import List, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """配置类"""
    
    # 服务器配置
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # ArXiv API配置
    ARXIV_API_BASE_URL = os.getenv("ARXIV_API_BASE_URL", "http://export.arxiv.org/api/query")
    ARXIV_MAX_RESULTS = int(os.getenv("ARXIV_MAX_RESULTS", "100"))
    ARXIV_REQUEST_TIMEOUT = int(os.getenv("ARXIV_REQUEST_TIMEOUT", "30"))
    
    # 知识库配置
    KNOWLEDGE_BASE_DATA_DIR = os.getenv("KNOWLEDGE_BASE_DATA_DIR", "./data/arxiv")
    KNOWLEDGE_BASE_CACHE_TTL = int(os.getenv("KNOWLEDGE_BASE_CACHE_TTL", "604800"))  # 7天
    KNOWLEDGE_BASE_UPDATE_INTERVAL = int(os.getenv("KNOWLEDGE_BASE_UPDATE_INTERVAL", "86400"))  # 24小时
    
    # 支持的论文分类
    @property
    def SUPPORTED_CATEGORIES(self) -> List[str]:
        categories_str = os.getenv("SUPPORTED_CATEGORIES", "cs.AI,cs.CV,cs.CL,cs.LG,cs.IR,cs.NE,stat.ML")
        return [cat.strip() for cat in categories_str.split(",") if cat.strip()]
    
    # 大模型配置
    LLM_MODEL_PATH = os.getenv("LLM_MODEL_PATH", "./models/qwen-7b")
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2048"))
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    
    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "./logs/app.log")
    
    # 缓存配置
    CACHE_ENABLED = os.getenv("CACHE_ENABLED", "True").lower() == "true"
    CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1小时
    
    # 数据库配置（可选）
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # 向量数据库配置（可选）
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./data/chroma")
    
    @classmethod
    def validate(cls) -> bool:
        """验证配置是否有效"""
        try:
            # 检查必要的配置
            if not cls.ARXIV_API_BASE_URL:
                raise ValueError("ARXIV_API_BASE_URL 不能为空")
            
            if cls.ARXIV_MAX_RESULTS <= 0:
                raise ValueError("ARXIV_MAX_RESULTS 必须大于0")
            
            if cls.ARXIV_REQUEST_TIMEOUT <= 0:
                raise ValueError("ARXIV_REQUEST_TIMEOUT 必须大于0")
            
            if not cls.SUPPORTED_CATEGORIES:
                raise ValueError("SUPPORTED_CATEGORIES 不能为空")
            
            return True
            
        except Exception as e:
            print(f"配置验证失败: {str(e)}")
            return False
    
    @classmethod
    def print_config(cls):
        """打印当前配置（敏感信息会隐藏）"""
        config_info = {
            "服务器配置": {
                "HOST": cls.HOST,
                "PORT": cls.PORT,
                "DEBUG": cls.DEBUG
            },
            "ArXiv API配置": {
                "ARXIV_API_BASE_URL": cls.ARXIV_API_BASE_URL,
                "ARXIV_MAX_RESULTS": cls.ARXIV_MAX_RESULTS,
                "ARXIV_REQUEST_TIMEOUT": cls.ARXIV_REQUEST_TIMEOUT
            },
            "知识库配置": {
                "KNOWLEDGE_BASE_DATA_DIR": cls.KNOWLEDGE_BASE_DATA_DIR,
                "KNOWLEDGE_BASE_CACHE_TTL": f"{cls.KNOWLEDGE_BASE_CACHE_TTL}秒",
                "KNOWLEDGE_BASE_UPDATE_INTERVAL": f"{cls.KNOWLEDGE_BASE_UPDATE_INTERVAL}秒",
                "SUPPORTED_CATEGORIES": cls.SUPPORTED_CATEGORIES
            },
            "大模型配置": {
                "LLM_MODEL_PATH": cls.LLM_MODEL_PATH,
                "LLM_MAX_TOKENS": cls.LLM_MAX_TOKENS,
                "LLM_TEMPERATURE": cls.LLM_TEMPERATURE
            },
            "日志配置": {
                "LOG_LEVEL": cls.LOG_LEVEL,
                "LOG_FILE": cls.LOG_FILE
            },
            "缓存配置": {
                "CACHE_ENABLED": cls.CACHE_ENABLED,
                "CACHE_TTL": f"{cls.CACHE_TTL}秒"
            }
        }
        
        print("=== 当前配置信息 ===")
        for category, settings in config_info.items():
            print(f"\n{category}:")
            for key, value in settings.items():
                print(f"  {key}: {value}")
        print("\n==================")

# 创建全局配置实例
config = Config()