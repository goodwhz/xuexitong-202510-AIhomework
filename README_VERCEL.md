# Vercel 部署指南

本文档说明如何将论文搜索引擎项目部署到 Vercel。

## 项目结构调整

按照 Vercel 的最佳实践，项目结构已调整为：

```
论文搜索引擎网站/
├── api/
│   └── index.py          # Vercel 无服务器函数入口
├── frontend/             # 前端静态文件
├── backend/              # 后端代码（保留原结构）
├── vercel.json           # Vercel 配置
└── requirements.txt      # Python 依赖
```

## 部署步骤

### 1. 环境准备

确保项目根目录包含以下文件：
- `vercel.json` - Vercel 配置
- `requirements.txt` - Python 依赖
- `api/index.py` - API 入口

### 2. 部署到 Vercel

#### 方法一：通过 Vercel CLI

```bash
# 安装 Vercel CLI
npm i -g vercel

# 登录 Vercel
vercel login

# 在项目根目录部署
cd 论文搜索引擎网站
vercel --prod
```

#### 方法二：通过 GitHub 集成

1. 将代码推送到 GitHub 仓库
2. 在 Vercel 控制台连接 GitHub 仓库
3. 配置环境变量
4. 自动部署

#### 方法三：通过 Vercel 网站上传

1. 访问 [vercel.com](https://vercel.com)
2. 点击 "New Project"
3. 选择 "Upload" 并上传项目文件夹

### 3. 环境变量配置

在 Vercel 控制台设置以下环境变量：

```env
HOST=0.0.0.0
PORT=3000
DEBUG=False
ARXIV_API_BASE_URL=http://export.arxiv.org/api/query
ARXIV_MAX_RESULTS=50
ARXIV_REQUEST_TIMEOUT=30
KNOWLEDGE_BASE_DATA_DIR=/tmp/data/arxiv
```

## 项目结构说明

### api/index.py

这是 Vercel 无服务器函数的入口点，使用 Mangum 适配 FastAPI：

```python
import sys
import os

# 添加后端目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# 导入 FastAPI 应用
from main import app

# 使用 Mangum 适配
from mangum import Mangum
handler = Mangum(app)

# Vercel 需要名为 'app' 的变量
app = handler
```

### vercel.json

Vercel 配置文件，定义了构建和路由规则：

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/index.py"
    },
    {
      "src": "/(.*)",
      "dest": "/api/index.py"
    }
  ],
  "functions": {
    "api/index.py": {
      "maxDuration": 30
    }
  }
}
```

## 故障排除

### 404 错误

如果遇到 404 错误，请检查：

1. **vercel.json 配置**：确保路由规则正确
2. **API 入口文件**：确认 `api/index.py` 存在且语法正确
3. **依赖安装**：检查 `requirements.txt` 中的依赖是否正确

### 构建失败

查看 Vercel 构建日志，常见问题：

1. **Python 版本不兼容**：Vercel 默认使用 Python 3.9
2. **依赖安装失败**：检查 requirements.txt 格式
3. **路径问题**：确保 Python 路径配置正确

### 运行时错误

查看函数日志，常见问题：

1. **环境变量缺失**：确保所有必需的环境变量已设置
2. **文件权限**：Vercel 文件系统是只读的，确保使用临时目录
3. **超时问题**：函数执行时间超过 30 秒限制

## 性能优化建议

1. **使用 CDN**：Vercel 自动提供全球 CDN
2. **缓存策略**：合理设置缓存头
3. **函数优化**：减少冷启动时间
4. **静态资源**：将静态文件托管在 Vercel 或 CDN

## 相关文档

- [Vercel 文档](https://vercel.com/docs)
- [FastAPI 部署指南](https://fastapi.tiangolo.com/deployment/)
- [Mangum 文档](https://mangum.io/)

---

如有问题，请查看 Vercel 控制台的构建和函数日志。