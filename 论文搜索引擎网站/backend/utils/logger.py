"""
日志配置工具
"""

import logging
import sys
from pathlib import Path
from loguru import logger as loguru_logger

def setup_logger(name: str = "paper_search_engine", level: str = "INFO") -> logging.Logger:
    """
    设置日志配置
    
    Args:
        name: 日志器名称
        level: 日志级别
        
    Returns:
        logging.Logger: 配置好的日志器
    """
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 移除默认的loguru处理器
    loguru_logger.remove()
    
    # 添加控制台输出
    loguru_logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=level,
        colorize=True
    )
    
    # 添加文件输出
    loguru_logger.add(
        log_dir / "app.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=level,
        rotation="1 day",
        retention="30 days",
        compression="zip"
    )
    
    # 添加错误日志文件
    loguru_logger.add(
        log_dir / "error.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="1 day",
        retention="30 days",
        compression="zip"
    )
    
    # 创建标准logging日志器
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # 添加loguru处理器
    class LoguruHandler(logging.Handler):
        def emit(self, record):
            try:
                level = loguru_logger.level(record.levelname).name
            except ValueError:
                level = record.levelno
            
            frame, depth = sys._getframe(6), 6
            while frame and frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1
            
            loguru_logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )
    
    logger.addHandler(LoguruHandler())
    
    return logger
