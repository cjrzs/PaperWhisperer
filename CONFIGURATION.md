# PaperWhisperer 配置指南

## 🔑 配置方式说明

**所有配置项都从环境变量中读取**

系统采用环境变量优先的配置策略：

1. **环境变量**（推荐用于生产环境）- 所有配置都通过环境变量读取
2. `.env` 文件（适合本地开发）- 启动时会自动加载 `.env` 文件到环境变量
3. 默认值 - 如果环境变量未设置，则使用默认值

**配置优先级**: 环境变量 > .env 文件 > 默认值

**注意**: 应用启动时会自动尝试加载项目根目录下的 `.env` 文件（如果存在）

## 🚀 快速开始

### 方式一：使用环境变量（推荐）

```bash
# 在 ~/.zshrc 或 ~/.bashrc 中添加
export QWEN_API_KEY="sk-your-actual-key"
export MINERU_TOKEN="your-actual-token"
export DEFAULT_LLM_PROVIDER="qwen"

# 重新加载配置
source ~/.zshrc  # 或 source ~/.bashrc

# 直接启动
./run.sh
```

**优点：**

- ✅ 更安全，不会误提交到 Git
- ✅ 适合多项目共享配置
- ✅ 符合 12-Factor App 最佳实践
- ✅ 生产环境标准做法

### 方式二：使用 .env 文件

```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件，去掉注释并填写实际的值
vim .env

# 启动服务
./run.sh
```

**优点：**

- ✅ 配置集中管理
- ✅ 适合本地开发调试

## 📋 必需配置项

### 1. LLM API Key（至少配置一个）

#### 通义千问（推荐）

```bash
export QWEN_API_KEY="sk-your-key"
```

- 获取地址：https://dashscope.aliyun.com/
- 优点：性价比高，中文效果好，API 稳定

#### OpenAI

```bash
export OPENAI_API_KEY="sk-your-key"
```

- 获取地址：https://platform.openai.com/

#### DeepSeek

```bash
export DEEPSEEK_API_KEY="sk-your-key"
```

- 获取地址：https://platform.deepseek.com/

### 2. MinerU Token（必需）

```bash
export MINERU_TOKEN="your-token"
```

- 获取地址：https://mineru.net/
- 用途：PDF 文档解析

## 🎛️ 可选配置项

### LLM API Base URLs（使用默认值即可）

```bash
export QWEN_API_BASE="https://dashscope.aliyuncs.com/compatible-mode/v1"
export OPENAI_API_BASE="https://api.openai.com/v1"
export DEEPSEEK_API_BASE="https://api.deepseek.com/v1"
```

### MinerU 配置

```bash
export MINERU_API_BASE="https://mineru.net/api/v4"
export MINERU_POLL_INTERVAL="3"  # 轮询间隔（秒）
export MINERU_TIMEOUT="600"  # 超时时间（秒）
```

### Milvus 向量数据库配置

```bash
export MILVUS_HOST="milvus"
export MILVUS_PORT="19530"
export MILVUS_COLLECTION_NAME="paper_chunks"
```

### 默认 LLM 提供商

```bash
export DEFAULT_LLM_PROVIDER="qwen"  # qwen, openai, deepseek
export DEFAULT_LLM_MODEL="qwen-max"
```

### 默认 Embedding 提供商

```bash
export DEFAULT_EMBEDDING_PROVIDER="qwen"  # qwen, openai
export DEFAULT_EMBEDDING_MODEL="text-embedding-v3"
```

### 应用服务配置

```bash
export BACKEND_PORT="8000"
export FRONTEND_PORT="80"
export MAX_UPLOAD_SIZE="50"  # 最大上传大小（MB）
export CHUNK_SIZE="800"  # 文本分块大小（tokens）
export CHUNK_OVERLAP="100"  # 文本分块重叠大小（tokens）
export TOP_K_RETRIEVAL="5"  # 检索返回的 Top K 结果数
```

### 路径配置（通常使用默认值）

```bash
export BASE_DIR="/app"
export DATA_DIR="/app/data"
export UPLOAD_DIR="/app/data/uploads"
export PARSED_DIR="/app/data/parsed"
export EMBEDDINGS_DIR="/app/data/embeddings"
export SUMMARIES_DIR="/app/data/summaries"
```

### 调试配置

```bash
export DEBUG="True"
export LOG_LEVEL="DEBUG"  # DEBUG, INFO, WARNING, ERROR
```

## 🔒 安全最佳实践

### 开发环境

```bash
# 1. 永远不要提交 .env 文件到 Git
# 2. 使用 .env.example 作为模板
# 3. 个人 API Key 只存在于本地环境变量
```

### 生产环境

```bash
# 1. 使用环境变量而不是 .env 文件
# 2. 使用密钥管理服务（如 AWS Secrets Manager）
# 3. 定期轮换 API Key
# 4. 使用最小权限原则
```

## 🔍 验证配置

启动服务后检查日志：

```bash
# 查看配置是否正确加载
docker-compose logs backend | grep -i "config"

# 查看完整日志
docker-compose logs -f backend
```

## 🆘 常见问题

### Q: 如何知道我的配置是否生效？

A: 启动脚本会检查必需的环境变量，如果缺少会给出提示。

### Q: 环境变量和 .env 文件可以混用吗？

A: 可以。环境变量会覆盖 .env 文件中的同名配置。

### Q: 如何在 Docker Compose 中使用环境变量？

A: Docker Compose 会自动读取宿主机的环境变量和 .env 文件。

### Q: 可以只配置一个 LLM 吗？

A: 可以。至少配置一个即可，其他的可以不配置。

## 📋 完整环境变量参考表

| 环境变量                     | 说明                       | 默认值                                              | 是否必需         |
| ---------------------------- | -------------------------- | --------------------------------------------------- | ---------------- |
| `QWEN_API_KEY`               | 通义千问 API Key           | 无                                                  | 至少需要一个 LLM |
| `QWEN_API_BASE`              | 通义千问 API Base URL      | `https://dashscope.aliyuncs.com/compatible-mode/v1` | 否               |
| `OPENAI_API_KEY`             | OpenAI API Key             | 无                                                  | 至少需要一个 LLM |
| `OPENAI_API_BASE`            | OpenAI API Base URL        | `https://api.openai.com/v1`                         | 否               |
| `DEEPSEEK_API_KEY`           | DeepSeek API Key           | 无                                                  | 至少需要一个 LLM |
| `DEEPSEEK_API_BASE`          | DeepSeek API Base URL      | `https://api.deepseek.com/v1`                       | 否               |
| `MINERU_TOKEN`               | MinerU API Token           | 无                                                  | 是（PDF 解析）   |
| `MINERU_API_BASE`            | MinerU API Base URL        | `https://mineru.net/api/v4`                         | 否               |
| `MINERU_POLL_INTERVAL`       | MinerU 轮询间隔（秒）      | `3`                                                 | 否               |
| `MINERU_TIMEOUT`             | MinerU 超时时间（秒）      | `600`                                               | 否               |
| `MILVUS_HOST`                | Milvus 主机地址            | `milvus`                                            | 否               |
| `MILVUS_PORT`                | Milvus 端口                | `19530`                                             | 否               |
| `MILVUS_COLLECTION_NAME`     | Milvus 集合名称            | `paper_chunks`                                      | 否               |
| `DEFAULT_LLM_PROVIDER`       | 默认 LLM 提供商            | `qwen`                                              | 否               |
| `DEFAULT_LLM_MODEL`          | 默认 LLM 模型              | `qwen-max`                                          | 否               |
| `DEFAULT_EMBEDDING_PROVIDER` | 默认 Embedding 提供商      | `qwen`                                              | 否               |
| `DEFAULT_EMBEDDING_MODEL`    | 默认 Embedding 模型        | `text-embedding-v3`                                 | 否               |
| `BACKEND_PORT`               | 后端服务端口               | `8000`                                              | 否               |
| `FRONTEND_PORT`              | 前端服务端口               | `80`                                                | 否               |
| `MAX_UPLOAD_SIZE`            | 最大上传文件大小（MB）     | `50`                                                | 否               |
| `CHUNK_SIZE`                 | 文本分块大小（tokens）     | `800`                                               | 否               |
| `CHUNK_OVERLAP`              | 文本分块重叠大小（tokens） | `100`                                               | 否               |
| `TOP_K_RETRIEVAL`            | 检索返回的 Top K 结果数    | `5`                                                 | 否               |
| `BASE_DIR`                   | 项目根目录                 | 自动检测                                            | 否               |
| `DATA_DIR`                   | 数据目录                   | `{BASE_DIR}/data`                                   | 否               |
| `UPLOAD_DIR`                 | 上传目录                   | `{DATA_DIR}/uploads`                                | 否               |
| `PARSED_DIR`                 | 解析结果目录               | `{DATA_DIR}/parsed`                                 | 否               |
| `EMBEDDINGS_DIR`             | 向量嵌入目录               | `{DATA_DIR}/embeddings`                             | 否               |
| `SUMMARIES_DIR`              | 摘要目录                   | `{DATA_DIR}/summaries`                              | 否               |
| `DEBUG`                      | 调试模式                   | `False`                                             | 否               |
| `LOG_LEVEL`                  | 日志级别                   | `INFO`                                              | 否               |

## 📚 更多信息

- [项目文档](README.md)
- [Docker 部署指南](docker-compose.yml)
- [API 文档](http://localhost:8000/docs)
