# ArXiv知识库集成指南

本文档详细介绍了如何在论文搜索引擎项目中集成ArXiv知识库，包括配置、API使用和最佳实践。

## 概述

ArXiv知识库将ArXiv论文数据库集成到项目中，提供以下功能：

- **论文搜索**: 基于关键词、分类、时间范围搜索ArXiv论文
- **论文详情**: 根据ArXiv ID获取论文详细信息
- **知识库管理**: 知识库的更新、统计和监控
- **智能问答**: 基于ArXiv论文内容的RAG问答系统

## 快速开始

### 1. 环境配置

复制环境变量模板文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置必要的参数：

```env
# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=True

# ArXiv API配置
ARXIV_API_BASE_URL=http://export.arxiv.org/api/query
ARXIV_MAX_RESULTS=100
ARXIV_REQUEST_TIMEOUT=30

# 知识库配置
KNOWLEDGE_BASE_DATA_DIR=./data/arxiv
KNOWLEDGE_BASE_CACHE_TTL=604800  # 7天
KNOWLEDGE_BASE_UPDATE_INTERVAL=86400  # 24小时

# 支持的论文分类
SUPPORTED_CATEGORIES=cs.AI,cs.CV,cs.CL,cs.LG,cs.IR,cs.NE,stat.ML
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 初始化知识库

```bash
cd backend
python scripts/init_knowledge_base.py
```

### 4. 启动服务

```bash
cd backend
python main.py
```

服务将在 http://localhost:8000 启动，API文档可在 http://localhost:8000/docs 查看。

## API接口

### 知识库统计

获取知识库的基本统计信息。

**请求:**
```http
GET /api/knowledge-base/stats
```

**响应:**
```json
{
  "last_updated": "2024-01-01T12:00:00",
  "total_papers": 1500,
  "cached_papers": 500,
  "categories": {
    "cs.AI": 300,
    "cs.CV": 250,
    "cs.CL": 200
  }
}
```

### 知识库搜索

搜索ArXiv论文。

**请求:**
```http
POST /api/knowledge-base/search
Content-Type: application/json

{
  "query": "machine learning",
  "max_results": 10,
  "categories": ["cs.AI", "cs.LG"],
  "year_from": 2020,
  "year_to": 2024
}
```

**响应:**
```json
{
  "papers": [
    {
      "arxiv_id": "2401.12345",
      "title": "Advanced Machine Learning Techniques",
      "authors": ["Author A", "Author B"],
      "abstract": "This paper presents...",
      "published": "2024-01-15",
      "categories": ["cs.AI", "cs.LG"],
      "pdf_url": "https://arxiv.org/pdf/2401.12345.pdf"
    }
  ],
  "total": 1,
  "query": "machine learning",
  "took": 0.85
}
```

### 获取论文详情

根据ArXiv ID获取论文详细信息。

**请求:**
```http
GET /api/knowledge-base/paper/2401.12345
```

**响应:**
```json
{
  "paper": {
    "arxiv_id": "2401.12345",
    "title": "Advanced Machine Learning Techniques",
    "authors": ["Author A", "Author B"],
    "abstract": "This paper presents...",
    "published": "2024-01-15",
    "categories": ["cs.AI", "cs.LG"],
    "pdf_url": "https://arxiv.org/pdf/2401.12345.pdf",
    "cached_at": "2024-01-21T10:30:00"
  }
}
```

### 分类论文查询

获取指定分类的最新论文。

**请求:**
```http
GET /api/knowledge-base/categories/cs.AI/papers?max_results=20&days=30
```

**响应:**
```json
{
  "category": "cs.AI",
  "papers": [
    {
      "arxiv_id": "2401.12345",
      "title": "Advanced Machine Learning Techniques",
      "authors": ["Author A", "Author B"],
      "abstract": "This paper presents...",
      "published": "2024-01-15",
      "categories": ["cs.AI"],
      "pdf_url": "https://arxiv.org/pdf/2401.12345.pdf"
    }
  ],
  "total": 1
}
```

### 热门论文

获取热门论文列表。

**请求:**
```http
GET /api/knowledge-base/trending?days=7
```

**响应:**
```json
{
  "trending_papers": [
    {
      "arxiv_id": "2401.12345",
      "title": "Advanced Machine Learning Techniques",
      "authors": ["Author A", "Author B"],
      "abstract": "This paper presents...",
      "published": "2024-01-15",
      "categories": ["cs.AI"],
      "pdf_url": "https://arxiv.org/pdf/2401.12345.pdf"
    }
  ],
  "total": 1,
  "days": 7
}
```

### 知识库更新

手动触发知识库更新。

**请求:**
```http
POST /api/knowledge-base/update
Content-Type: application/json

{
  "categories": ["cs.AI", "cs.CV"],
  "force_update": false
}
```

**响应:**
```json
{
  "success": true,
  "message": "知识库更新任务已启动，将在后台执行",
  "task_id": "update_task_001"
}
```

## 配置说明

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `ARXIV_API_BASE_URL` | `http://export.arxiv.org/api/query` | ArXiv API基础URL |
| `ARXIV_MAX_RESULTS` | `100` | 单次搜索最大结果数 |
| `ARXIV_REQUEST_TIMEOUT` | `30` | API请求超时时间（秒） |
| `KNOWLEDGE_BASE_DATA_DIR` | `./data/arxiv` | 知识库数据存储目录 |
| `KNOWLEDGE_BASE_CACHE_TTL` | `604800` | 缓存生存时间（秒） |
| `KNOWLEDGE_BASE_UPDATE_INTERVAL` | `86400` | 知识库更新间隔（秒） |
| `SUPPORTED_CATEGORIES` | `cs.AI,cs.CV,cs.CL,cs.LG,cs.IR,cs.NE,stat.ML` | 支持的论文分类 |

### 支持的论文分类

- `cs.AI` - 人工智能
- `cs.CV` - 计算机视觉
- `cs.CL` - 计算语言学
- `cs.LG` - 机器学习
- `cs.IR` - 信息检索
- `cs.NE` - 神经网络
- `stat.ML` - 统计机器学习
- `cs.RO` - 机器人学
- `cs.CC` - 计算复杂性
- `cs.DS` - 数据结构

## 高级功能

### 1. 向量搜索集成

项目支持与向量数据库（如ChromaDB）集成，提供更精确的语义搜索：

```python
from services.arxiv_knowledge_base import ArxivKnowledgeBase

knowledge_base = ArxivKnowledgeBase()

# 启用向量搜索
if knowledge_base.vector_store.is_available():
    results = await knowledge_base.search_papers("machine learning", use_vector=True)
```

### 2. 缓存策略

知识库实现智能缓存策略：

- **论文详情缓存**: 7天自动过期
- **搜索结果缓存**: 1小时缓存时间
- **分类统计缓存**: 24小时更新间隔

### 3. 后台更新任务

知识库支持后台自动更新：

```python
# 手动触发更新
await knowledge_base.update_knowledge_base()

# 定时更新（需要外部调度）
# 建议使用cron job或celery beat
```

## 最佳实践

### 1. 搜索优化

- 使用具体的搜索关键词
- 结合分类筛选提高精度
- 合理设置时间范围

```python
# 好的搜索示例
results = await knowledge_base.search_papers(
    query="transformer architecture",
    categories=["cs.CL", "cs.LG"],
    year_from=2020,
    max_results=20
)
```

### 2. 错误处理

```python
try:
    papers = await knowledge_base.search_papers(query)
except Exception as e:
    logger.error(f"搜索失败: {str(e)}")
    # 返回空结果或默认值
    papers = []
```

### 3. 性能优化

- 合理设置缓存时间
- 使用分页避免一次性加载过多数据
- 考虑使用CDN缓存静态资源

## 故障排除

### 常见问题

1. **API请求失败**
   - 检查网络连接
   - 验证ArXiv API是否可访问
   - 检查请求频率是否过高

2. **搜索结果为空**
   - 检查搜索关键词是否正确
   - 验证分类名称是否支持
   - 检查时间范围设置

3. **缓存问题**
   - 清除缓存目录重新初始化
   - 检查文件权限
   - 验证磁盘空间

### 日志调试

启用DEBUG级别日志获取详细调试信息：

```env
LOG_LEVEL=DEBUG
```

## 扩展开发

### 添加新的论文源

可以扩展`ArxivKnowledgeBase`类来支持其他论文数据库：

```python
class MultiSourceKnowledgeBase(ArxivKnowledgeBase):
    async def search_papers(self, query, sources=["arxiv", "acl"]):
        # 实现多源搜索逻辑
        pass
```

### 自定义搜索算法

重写排序和筛选逻辑：

```python
def _sort_papers(self, papers, query):
    # 实现自定义排序算法
    return sorted_papers
```

## 相关文档

- [API文档](API文档.md)
- [部署指南](部署指南.md) 
- [技术实现文档](技术实现文档.md)
- [用户指南](用户指南.md)

---

如有问题，请查看项目文档或提交Issue。