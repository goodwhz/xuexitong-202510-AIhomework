"""
Vercel Serverless Function for FastAPI
This file handles API requests for Vercel deployment
"""

from fastapi import FastAPI
from mangum import Mangum

# 创建简单的FastAPI应用
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "论文搜索引擎API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "服务运行正常"}

@app.get("/search")
async def search_papers(q: str = "", limit: int = 10):
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

# Create handler for Vercel
handler = Mangum(app)

# Vercel expects the handler to be named 'app'
app = handler