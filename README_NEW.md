# 📄 PaperWhisperer - 智能论文助手

> "Listen to what papers are whispering to you."

PaperWhisperer 是一个基于 AI 的智能论文助手，帮助你深度理解学术论文。上传 PDF 或粘贴论文链接，即可获得高质量翻译、智能摘要和基于论文内容的深度对话。

## ✨ 核心功能

- 📖 **智能 PDF 解析** - 使用 MinerU API 自动提取论文结构、章节和元数据
- 🌐 **高质量翻译** - 专业学术论文翻译，保持术语准确性和语句流畅性
- 📋 **智能摘要生成** - Map-Reduce 策略生成综合摘要和关键要点
- 💬 **RAG 对话问答** - 基于论文内容的智能问答，支持引用溯源
- 🔍 **向量检索** - 使用 Milvus 进行高效的语义搜索

## 🏗️ 技术架构

### 后端技术栈

- **框架**: FastAPI (Python 3.11)
- **向量数据库**: Milvus 2.3.3
- **LLM 提供商**: Qwen / OpenAI / DeepSeek (多提供商支持)
- **PDF 解析**: MinerU API
- **文本处理**: tiktoken, 自定义分块算法

### 前端技术栈

- **框架**: Vue 3 + Vite
- **状态管理**: Pinia
- **路由**: Vue Router
- **UI 库**: Tailwind CSS + DaisyUI
- **HTTP 客户端**: Axios

### 部署方案

- **容器化**: Docker + Docker Compose
- **服务编排**: Milvus (Standalone) + Backend + Frontend
- **反向代理**: Nginx

## 🚀 快速开始

### 前置要求

- Docker 和 Docker Compose
- 至少 4GB 可用内存
- API Keys：
  - MinerU Token
  - Qwen API Key (或 OpenAI / DeepSeek)

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/PaperWhisperer.git
cd PaperWhisperer
```

### 2. 配置环境变量

**方式一：使用环境变量（推荐用于生产环境）**

在你的 shell 配置文件（`~/.zshrc` 或 `~/.bashrc`）中添加：

```bash
# 必需配置
export QWEN_API_KEY="sk-your-qwen-api-key"
export MINERU_TOKEN="your-mineru-token"

# 可选配置
export DEFAULT_LLM_PROVIDER="qwen"
export DEFAULT_EMBEDDING_PROVIDER="qwen"
```

然后重新加载配置：

```bash
source ~/.zshrc  # 或 source ~/.bashrc
```

**方式二：使用 .env 文件（推荐用于本地开发）**

复制环境变量配置模板：

```bash
cp env.example.txt .env
```

编辑 `.env` 文件，填入你的 API Keys：

```env
# LLM API Keys（至少配置一个）
QWEN_API_KEY=sk-your-qwen-api-key
# OPENAI_API_KEY=sk-your-openai-api-key  # 可选
# DEEPSEEK_API_KEY=sk-your-deepseek-api-key  # 可选

# MinerU（必需）
MINERU_TOKEN=your-mineru-token

# 默认设置（可选，已有默认值）
# DEFAULT_LLM_PROVIDER=qwen
# DEFAULT_EMBEDDING_PROVIDER=qwen
```

**完整的环境变量列表请查看 [CONFIGURATION.md](CONFIGURATION.md) 或 [env.example.txt](env.example.txt)**

### 3. 启动服务

```bash
chmod +x run.sh
./run.sh
```

或者手动启动：

```bash
docker-compose up -d
```

### 4. 访问应用

- **前端界面**: http://localhost
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **Milvus**: localhost:19530
- **MinIO 控制台**: http://localhost:9001

## 📖 使用指南

### 上传论文

1. 访问首页
2. 选择以下任一方式：
   - 上传本地 PDF 文件（最大 50MB）
   - 输入论文 URL（如 arXiv 链接）
3. 等待自动解析（通常需要 1-3 分钟）

### 查看论文

解析完成后，你可以：

- **原文视图** - 查看论文的结构化内容
- **翻译视图** - 生成高质量中文翻译（双语对照 / 仅译文 / 仅原文）
- **摘要视图** - 查看智能生成的综合摘要、关键要点、方法和贡献
- **对话视图** - 与 AI 助手对话，询问关于论文的任何问题

### API 使用

#### 上传论文

```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@paper.pdf"
```

#### 翻译论文

```bash
curl -X POST "http://localhost:8000/api/translate/{paper_id}"
```

#### 生成摘要

```bash
curl -X POST "http://localhost:8000/api/summary/{paper_id}"
```

#### 对话问答

```bash
curl -X POST "http://localhost:8000/api/chat/{paper_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "这篇论文的主要贡献是什么？",
    "session_id": null
  }'
```

更多 API 详情请查看：http://localhost:8000/docs

## 🔧 开发指南

### 项目结构

```
PaperWhisperer/
├── app/                          # 后端代码
│   ├── main.py                   # FastAPI 入口
│   ├── config.py                 # 配置管理
│   ├── routers/                  # API 路由
│   │   ├── upload.py
│   │   ├── translate.py
│   │   ├── summary.py
│   │   └── chat.py
│   ├── services/                 # 业务逻辑
│   │   ├── mineru_client.py
│   │   ├── paper_parser.py
│   │   ├── llm_factory.py
│   │   ├── embedding_service.py
│   │   ├── milvus_service.py
│   │   ├── text_processor.py
│   │   ├── vectorization_service.py
│   │   ├── translator.py
│   │   ├── summarizer.py
│   │   └── rag_service.py
│   ├── utils/                    # 工具函数
│   └── models/                   # 数据模型
├── frontend/                     # 前端代码
│   ├── src/
│   │   ├── views/
│   │   ├── components/
│   │   ├── stores/
│   │   ├── api/
│   │   └── router/
│   └── Dockerfile
├── data/                         # 数据存储
│   ├── uploads/
│   ├── parsed/
│   ├── embeddings/
│   └── summaries/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

### 本地开发

#### 后端开发

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
cd app
python main.py
```

#### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 运行测试

```bash
# 后端测试
pytest tests/

# 前端测试
cd frontend
npm run test
```

## 📊 性能优化

### 建议配置

- **CPU**: 4 核以上
- **内存**: 8GB 以上（Milvus 需要约 2-3GB）
- **磁盘**: 20GB 以上可用空间

### 优化建议

1. **向量化缓存** - 已解析的论文向量会缓存在 Milvus 中
2. **异步处理** - 解析、翻译、摘要等耗时任务使用后台任务
3. **批量 Embedding** - 文本块批量生成向量以提高效率
4. **连接池** - 数据库连接复用

## 🛠️ 故障排除

### Milvus 连接失败

```bash
# 检查 Milvus 是否正常运行
docker-compose logs milvus

# 重启 Milvus
docker-compose restart milvus
```

### 内存不足

如果系统内存有限，可以调整 Milvus 配置或使用 Milvus Lite。

### API 限流

如果遇到 LLM API 限流，可以：

1. 降低并发请求数
2. 增加重试间隔
3. 切换到其他提供商

## 📝 待办事项

- [ ] 支持更多论文来源（IEEE、SpringerLink 等）
- [ ] 批量论文处理
- [ ] 论文对比分析功能
- [ ] 导出功能（Markdown、PDF）
- [ ] 用户系统和论文管理
- [ ] 更多 LLM 提供商支持
- [ ] 移动端适配

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 开源协议

MIT License © 2025

## 🙏 致谢

- [MinerU](https://mineru.net/) - 优秀的 PDF 解析服务
- [Milvus](https://milvus.io/) - 高性能向量数据库
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化 Python Web 框架
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架

---

**如有问题或建议，欢迎联系我们！**
