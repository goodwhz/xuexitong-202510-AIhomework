"""
论文搜索引擎后端主程序
基于FastAPI构建的RESTful API服务
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv

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

@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "message": "论文搜索引擎API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "message": "服务运行正常"}

@app.get("/api/search")
@app.post("/api/search")
async def search_papers(q: str = "", limit: int = 10):
    """搜索论文接口"""
    return {
        "query": q,
        "limit": limit,
        "results": [
            {
                "id": "2401.12345",
                "title": "深度学习在自然语言处理中的应用",
                "authors": ["张三", "李四"],
                "abstract": "本文探讨了深度学习技术在自然语言处理领域的应用...",
                "published": "2024-01-15",
                "categories": ["cs.CL", "cs.AI"]
            }
        ],
        "total": 1
    }

@app.get("/api/paper/{paper_id}")
async def get_paper(paper_id: str):
    """获取论文详情"""
    return {
        "paper_id": paper_id,
        "title": "深度学习在自然语言处理中的应用",
        "authors": ["张三", "李四"],
        "abstract": "本文探讨了深度学习技术在自然语言处理领域的应用...",
        "published": "2024-01-15",
        "categories": ["cs.CL", "cs.AI"],
        "pdf_url": f"https://arxiv.org/pdf/{paper_id}.pdf"
    }

@app.post("/api/qa")
async def ask_question(question: str):
    """智能问答接口"""
    return {
        "question": question,
        "answer": "根据相关研究，这个问题可以从以下几个方面来理解...",
        "sources": [
            {
                "title": "深度学习在自然语言处理中的应用",
                "url": "https://arxiv.org/abs/2401.12345"
            }
        ]
    }

@app.get("/api/search/suggestions")
async def get_search_suggestions(q: str = ""):
    """搜索建议接口"""
    return {
        "suggestions": ["机器学习", "深度学习", "自然语言处理", "计算机视觉"]
    }

@app.get("/api/search/trending")
async def get_trending_topics():
    """热门话题接口"""
    return {
        "topics": ["人工智能", "大语言模型", "强化学习", "联邦学习"]
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    return JSONResponse(
        status_code=500,
        content={"message": "服务器内部错误", "detail": str(exc)}
    )

if __name__ == "__main__":
    # 获取配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8001))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    print(f"启动服务器: {host}:{port}")
    
    # 启动服务器
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )