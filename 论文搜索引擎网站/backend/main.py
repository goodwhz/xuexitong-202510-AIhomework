"""
论文搜索引擎后端主程序
基于FastAPI构建的RESTful API服务
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv

from api.search import router as search_router
from api.paper import router as paper_router
from api.qa import router as qa_router
from utils.logger import setup_logger

# 加载环境变量
load_dotenv()

# 创建FastAPI应用
app = FastAPI(
    title="论文搜索引擎API",
    description="基于RAG技术的智能论文搜索引擎",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 设置日志
logger = setup_logger()

# 注册路由
app.include_router(search_router, prefix="/api/search", tags=["搜索"])
app.include_router(paper_router, prefix="/api/paper", tags=["论文"])
app.include_router(qa_router, prefix="/api/qa", tags=["问答"])

@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "message": "论文搜索引擎API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "message": "服务运行正常"}

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    logger.error(f"全局异常: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"message": "服务器内部错误", "detail": str(exc)}
    )

if __name__ == "__main__":
    # 获取配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    logger.info(f"启动服务器: {host}:{port}")
    
    # 启动服务器
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
