# 论文搜索引擎网站

一个基于RAG（检索增强生成）技术的智能论文搜索引擎，支持论文搜索、下载和智能问答功能。

## 项目特性

- 🔍 **智能搜索**: 基于RAG技术的语义搜索
- 📚 **ArXiv集成**: 支持ArXiv论文库检索
- 🤖 **本地LLM**: 使用Qwen模型进行本地推理
- 🔗 **可追溯引用**: 支持引用来源追踪
- 🌐 **在线部署**: 支持Netlify部署
- 📱 **响应式设计**: 适配各种设备
- 💬 **Dify AI助手**: 集成Dify智能聊天机器人

## 技术栈

### 后端
- **Python 3.8+**
- **LangChain 0.3**: 大模型编排框架
- **Qwen**: 本地部署的大语言模型
- **FastAPI**: Web框架
- **ArXiv API**: 论文数据源
- **ChromaDB**: 向量数据库

### 前端
- **HTML5/CSS3/JavaScript**
- **Bootstrap**: UI框架
- **Axios**: HTTP客户端

### 部署
- **Netlify**: 静态网站托管
- **API调用**: 在线LLM服务

## 项目结构

```
论文搜索引擎网站/
├── backend/           # 后端代码
│   ├── models/        # 模型相关
│   ├── services/      # 业务逻辑
│   ├── api/          # API接口
│   └── utils/        # 工具函数
├── frontend/         # 前端代码
│   ├── static/       # 静态资源
│   ├── templates/    # 模板文件
│   └── js/          # JavaScript文件
├── docs/           # 文档
└── requirements.txt # 依赖包
```

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 本地开发

```bash
# 启动后端服务
cd backend
python main.py

# 启动前端服务
cd frontend
python -m http.server 8000
```

### 3. 部署到Netlify

1. 将项目推送到GitHub
2. 在Netlify中连接GitHub仓库
3. 配置构建设置
4. 部署完成

## 功能说明

### 论文搜索
- 支持关键词搜索
- 支持语义搜索
- 支持高级筛选

### 智能问答
- 基于RAG的问答系统
- 支持上下文理解
- 提供引用来源

### 论文下载
- 支持PDF下载
- 支持批量下载
- 支持格式转换

## 开发计划

- [x] 项目基础结构搭建
- [ ] 本地Qwen模型部署
- [ ] LangChain集成
- [ ] RAG流水线构建
- [ ] 前端界面开发
- [ ] 论文下载功能
- [ ] Netlify部署
- [ ] 技术文档编写

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT License

## 联系方式

如有问题，请提交Issue或联系开发者。
