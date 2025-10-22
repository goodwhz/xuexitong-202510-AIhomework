# 论文搜索引擎 API 文档

## 概述

本文档详细描述了论文搜索引擎系统的API接口，包括论文搜索、下载和智能问答功能。

## 基础信息

- **Base URL**: `http://localhost:8000/api` (开发环境)
- **Content-Type**: `application/json`
- **字符编码**: UTF-8

## 认证

当前版本不需要认证，未来版本将支持API密钥认证。

## 通用响应格式

### 成功响应
```json
{
  "status": "success",
  "data": { ... },
  "message": "操作成功"
}
```

### 错误响应
```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": { ... }
  }
}
```

## API 端点

### 1. 论文搜索

#### 搜索论文
```http
GET /api/search?query={query}&max_results={max_results}
```

**参数:**
- `query` (string, required): 搜索关键词或短语
- `max_results` (integer, optional): 最大返回结果数，默认10，范围1-50

**响应示例:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "2301.12345",
      "title": "Deep Learning for Natural Language Processing",
      "authors": ["John Doe", "Jane Smith"],
      "summary": "This paper presents a novel approach to...",
      "published": "2023-01-15",
      "pdf_url": "https://arxiv.org/pdf/2301.12345.pdf",
      "primary_category": "cs.CL",
      "categories": ["cs.CL", "cs.AI"]
    }
  ],
  "message": "搜索完成"
}
```

**错误码:**
- `INVALID_QUERY`: 查询参数无效
- `SEARCH_FAILED`: 搜索失败
- `RATE_LIMIT_EXCEEDED`: 请求频率超限

### 2. 论文下载

#### 下载论文PDF
```http
GET /api/paper/download/{paper_id}
```

**参数:**
- `paper_id` (string, required): 论文ID

**响应:**
- 成功: 返回PDF文件流
- 失败: 返回错误JSON

**响应头:**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="paper_id.pdf"
```

**错误码:**
- `PAPER_NOT_FOUND`: 论文不存在
- `DOWNLOAD_FAILED`: 下载失败
- `FILE_NOT_AVAILABLE`: 文件不可用

### 3. 智能问答

#### 提交问题
```http
POST /api/qa/ask
```

**请求体:**
```json
{
  "question": "什么是深度学习？",
  "context": "optional context",
  "max_tokens": 500
}
```

**参数:**
- `question` (string, required): 用户问题
- `context` (string, optional): 上下文信息
- `max_tokens` (integer, optional): 最大生成token数，默认500

**响应示例:**
```json
{
  "status": "success",
  "data": {
    "answer": "深度学习是机器学习的一个分支...",
    "citations": [
      {
        "paper_id": "2301.12345",
        "title": "Deep Learning for Natural Language Processing",
        "url": "https://arxiv.org/pdf/2301.12345.pdf",
        "relevance_score": 0.95
      }
    ],
    "confidence": 0.87,
    "processing_time": 2.3
  },
  "message": "回答生成完成"
}
```

**错误码:**
- `INVALID_QUESTION`: 问题格式无效
- `LLM_ERROR`: LLM处理错误
- `CONTEXT_TOO_LONG`: 上下文过长
- `RATE_LIMIT_EXCEEDED`: 请求频率超限

### 4. 系统状态

#### 健康检查
```http
GET /api/health
```

**响应示例:**
```json
{
  "status": "healthy",
  "timestamp": "2023-01-15T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "llm": "healthy",
    "vector_store": "healthy"
  }
}
```

#### 系统信息
```http
GET /api/info
```

**响应示例:**
```json
{
  "name": "论文搜索引擎",
  "version": "1.0.0",
  "description": "基于RAG的论文搜索和问答系统",
  "features": [
    "论文搜索",
    "PDF下载",
    "智能问答",
    "引用追踪"
  ],
  "llm_model": "Qwen-7B-Chat",
  "vector_store": "ChromaDB"
}
```

## 高级功能

### 1. 批量搜索

#### 批量搜索论文
```http
POST /api/search/batch
```

**请求体:**
```json
{
  "queries": [
    "machine learning",
    "deep learning",
    "natural language processing"
  ],
  "max_results_per_query": 5
}
```

**响应示例:**
```json
{
  "status": "success",
  "data": {
    "results": [
      {
        "query": "machine learning",
        "papers": [ ... ],
        "total_found": 15
      }
    ],
    "total_queries": 3,
    "processing_time": 5.2
  }
}
```

### 2. 论文推荐

#### 获取相关论文
```http
GET /api/paper/{paper_id}/recommendations?limit={limit}
```

**参数:**
- `paper_id` (string, required): 论文ID
- `limit` (integer, optional): 推荐数量，默认5

**响应示例:**
```json
{
  "status": "success",
  "data": {
    "recommendations": [
      {
        "paper_id": "2301.12346",
        "title": "Related Paper Title",
        "similarity_score": 0.89,
        "reason": "Similar topics and methodology"
      }
    ]
  }
}
```

### 3. 搜索历史

#### 获取搜索历史
```http
GET /api/search/history?limit={limit}
```

**参数:**
- `limit` (integer, optional): 返回数量，默认20

**响应示例:**
```json
{
  "status": "success",
  "data": {
    "searches": [
      {
        "query": "deep learning",
        "timestamp": "2023-01-15T10:30:00Z",
        "result_count": 15
      }
    ]
  }
}
```

## 错误处理

### HTTP状态码

| 状态码 | 描述 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 429 | 请求频率超限 |
| 500 | 服务器内部错误 |
| 503 | 服务不可用 |

### 错误响应格式

```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {
      "field": "specific field error",
      "timestamp": "2023-01-15T10:30:00Z"
    }
  }
}
```

### 常见错误码

| 错误码 | HTTP状态码 | 描述 |
|--------|------------|------|
| `INVALID_PARAMETER` | 400 | 参数无效 |
| `MISSING_REQUIRED_FIELD` | 400 | 缺少必需字段 |
| `QUERY_TOO_SHORT` | 400 | 查询太短 |
| `QUERY_TOO_LONG` | 400 | 查询太长 |
| `MAX_RESULTS_EXCEEDED` | 400 | 结果数量超限 |
| `PAPER_NOT_FOUND` | 404 | 论文不存在 |
| `RATE_LIMIT_EXCEEDED` | 429 | 请求频率超限 |
| `LLM_SERVICE_UNAVAILABLE` | 503 | LLM服务不可用 |
| `VECTOR_STORE_ERROR` | 500 | 向量存储错误 |
| `INTERNAL_SERVER_ERROR` | 500 | 服务器内部错误 |

## 限流和配额

### 请求限制

| 端点 | 限制 | 时间窗口 |
|------|------|----------|
| `/api/search` | 100次/分钟 | 1分钟 |
| `/api/qa/ask` | 20次/分钟 | 1分钟 |
| `/api/paper/download` | 50次/分钟 | 1分钟 |

### 配额响应头

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248600
```

## 数据模型

### 论文对象 (Paper)

```json
{
  "id": "string",
  "title": "string",
  "authors": ["string"],
  "summary": "string",
  "published": "string (YYYY-MM-DD)",
  "pdf_url": "string (URL)",
  "primary_category": "string",
  "categories": ["string"],
  "doi": "string (optional)",
  "abstract": "string (optional)",
  "keywords": ["string"] (optional)
}
```

### 引用对象 (Citation)

```json
{
  "paper_id": "string",
  "title": "string",
  "url": "string",
  "relevance_score": "number (0-1)",
  "page_number": "number (optional)",
  "section": "string (optional)"
}
```

### 问答响应 (QA Response)

```json
{
  "answer": "string",
  "citations": [Citation],
  "confidence": "number (0-1)",
  "processing_time": "number (seconds)",
  "model_used": "string",
  "tokens_used": "number"
}
```

## 使用示例

### JavaScript示例

```javascript
// 搜索论文
async function searchPapers(query) {
  try {
    const response = await fetch(`/api/search?query=${encodeURIComponent(query)}`);
    const data = await response.json();
    return data.data;
  } catch (error) {
    console.error('搜索失败:', error);
    throw error;
  }
}

// 下载论文
async function downloadPaper(paperId) {
  try {
    const response = await fetch(`/api/paper/download/${paperId}`);
    if (response.ok) {
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${paperId}.pdf`;
      a.click();
    } else {
      throw new Error('下载失败');
    }
  } catch (error) {
    console.error('下载失败:', error);
    throw error;
  }
}

// 智能问答
async function askQuestion(question) {
  try {
    const response = await fetch('/api/qa/ask', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question }),
    });
    const data = await response.json();
    return data.data;
  } catch (error) {
    console.error('问答失败:', error);
    throw error;
  }
}
```

### Python示例

```python
import requests
import json

class PaperSearchAPI:
    def __init__(self, base_url="http://localhost:8000/api"):
        self.base_url = base_url
    
    def search_papers(self, query, max_results=10):
        """搜索论文"""
        url = f"{self.base_url}/search"
        params = {"query": query, "max_results": max_results}
        response = requests.get(url, params=params)
        return response.json()
    
    def download_paper(self, paper_id):
        """下载论文PDF"""
        url = f"{self.base_url}/paper/download/{paper_id}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"下载失败: {response.status_code}")
    
    def ask_question(self, question):
        """智能问答"""
        url = f"{self.base_url}/qa/ask"
        data = {"question": question}
        response = requests.post(url, json=data)
        return response.json()

# 使用示例
api = PaperSearchAPI()

# 搜索论文
papers = api.search_papers("machine learning")
print(f"找到 {len(papers['data'])} 篇论文")

# 智能问答
qa_response = api.ask_question("什么是深度学习？")
print(f"回答: {qa_response['data']['answer']}")
```

### cURL示例

```bash
# 搜索论文
curl -X GET "http://localhost:8000/api/search?query=machine%20learning&max_results=5"

# 下载论文
curl -X GET "http://localhost:8000/api/paper/download/2301.12345" -o paper.pdf

# 智能问答
curl -X POST "http://localhost:8000/api/qa/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "什么是深度学习？"}'

# 健康检查
curl -X GET "http://localhost:8000/api/health"
```

## 版本控制

### API版本

当前版本: `v1.0.0`

### 版本兼容性

- 向后兼容: 是
- 废弃功能: 无
- 新功能: 定期更新

### 版本升级

API版本通过URL路径指定:
```
http://localhost:8000/api/v1/search
```

## 性能指标

### 响应时间

| 端点 | 平均响应时间 | 95%响应时间 |
|------|-------------|-------------|
| `/api/search` | 200ms | 500ms |
| `/api/qa/ask` | 2s | 5s |
| `/api/paper/download` | 1s | 3s |

### 吞吐量

- 搜索请求: 100 QPS
- 问答请求: 10 QPS
- 下载请求: 50 QPS

## 监控和日志

### 日志级别

- `DEBUG`: 详细调试信息
- `INFO`: 一般信息
- `WARNING`: 警告信息
- `ERROR`: 错误信息
- `CRITICAL`: 严重错误

### 监控指标

- 请求数量
- 响应时间
- 错误率
- 系统资源使用率

## 安全考虑

### 输入验证

- 所有输入参数都经过验证
- SQL注入防护
- XSS攻击防护
- 文件上传安全检查

### 访问控制

- IP白名单（可选）
- API密钥认证（未来版本）
- 请求频率限制

### 数据保护

- 敏感数据加密
- 日志脱敏
- 数据备份和恢复

## 故障排除

### 常见问题

1. **搜索无结果**
   - 检查查询关键词
   - 尝试不同的搜索词
   - 检查网络连接

2. **下载失败**
   - 检查论文ID是否正确
   - 检查网络连接
   - 检查服务器状态

3. **问答无响应**
   - 检查LLM服务状态
   - 检查问题格式
   - 检查系统资源

### 调试信息

启用调试模式获取详细日志:
```bash
export DEBUG=True
export LOG_LEVEL=DEBUG
```

## 联系支持

- 技术支持: support@example.com
- 文档问题: docs@example.com
- 功能建议: feedback@example.com

## 更新日志

### v1.0.0 (2023-01-15)
- 初始版本发布
- 基础搜索功能
- PDF下载功能
- 智能问答功能
- 引用追踪功能
