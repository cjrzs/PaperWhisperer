# 环境变量配置说明

## 概述

PaperWhisperer 的所有配置现在都通过**环境变量**进行管理。这符合[12-Factor App](https://12factor.net/config)的最佳实践，使配置更加灵活和安全。

## 配置方式

### 方式一：直接设置环境变量（推荐）

在你的 shell 配置文件中（`~/.zshrc` 或 `~/.bashrc`）添加：

```bash
export QWEN_API_KEY="sk-your-qwen-api-key"
export MINERU_TOKEN="your-mineru-token"
export DEFAULT_LLM_PROVIDER="qwen"
```

然后重新加载：

```bash
source ~/.zshrc  # 或 source ~/.bashrc
```

### 方式二：使用 .env 文件

1. 在项目根目录创建 `.env` 文件（可以复制 `env.example.txt`）
2. 填写配置项
3. 启动应用时会自动加载

**注意**: 不要将 `.env` 文件提交到 Git！

## 配置项列表

### 必需配置

#### LLM API Key（至少配置一个）

```bash
# 通义千问
export QWEN_API_KEY="sk-your-key"

# OpenAI
export OPENAI_API_KEY="sk-your-key"

# DeepSeek
export DEEPSEEK_API_KEY="sk-your-key"
```

#### MinerU Token（必需）

```bash
export MINERU_TOKEN="your-token"
```

### 可选配置

#### LLM API Base URLs

```bash
export QWEN_API_BASE="https://dashscope.aliyuncs.com/compatible-mode/v1"
export OPENAI_API_BASE="https://api.openai.com/v1"
export DEEPSEEK_API_BASE="https://api.deepseek.com/v1"
```

#### MinerU 配置

```bash
export MINERU_API_BASE="https://mineru.net/api/v4"
export MINERU_POLL_INTERVAL="3"  # 轮询间隔（秒）
export MINERU_TIMEOUT="600"  # 超时时间（秒）
```

#### Milvus 向量数据库

```bash
export MILVUS_HOST="milvus"
export MILVUS_PORT="19530"
export MILVUS_COLLECTION_NAME="paper_chunks"
```

#### 默认提供商

```bash
export DEFAULT_LLM_PROVIDER="qwen"  # qwen, openai, deepseek
export DEFAULT_LLM_MODEL="qwen-max"
export DEFAULT_EMBEDDING_PROVIDER="qwen"  # qwen, openai
export DEFAULT_EMBEDDING_MODEL="text-embedding-v3"
```

#### 应用服务配置

```bash
export BACKEND_PORT="8000"
export FRONTEND_PORT="80"
export MAX_UPLOAD_SIZE="50"  # 最大上传大小（MB）
export CHUNK_SIZE="800"  # 文本分块大小（tokens）
export CHUNK_OVERLAP="100"  # 文本分块重叠大小（tokens）
export TOP_K_RETRIEVAL="5"  # 检索返回的 Top K 结果数
```

#### 路径配置

```bash
export BASE_DIR="/app"
export DATA_DIR="/app/data"
export UPLOAD_DIR="/app/data/uploads"
export PARSED_DIR="/app/data/parsed"
export EMBEDDINGS_DIR="/app/data/embeddings"
export SUMMARIES_DIR="/app/data/summaries"
```

#### 调试配置

```bash
export DEBUG="True"
export LOG_LEVEL="DEBUG"  # DEBUG, INFO, WARNING, ERROR
```

## 完整的环境变量参考表

详见 [CONFIGURATION.md](CONFIGURATION.md) 中的完整参考表。

## Docker Compose 使用

在 `docker-compose.yml` 中，环境变量会自动从宿主机传递到容器：

```yaml
environment:
  - QWEN_API_KEY=${QWEN_API_KEY}
  - MINERU_TOKEN=${MINERU_TOKEN}
  # ... 其他配置
```

## 验证配置

启动应用后，检查日志确认配置是否正确加载：

```bash
docker-compose logs backend | head -20
```

你应该看到类似的输出：

```
PaperWhisperer 正在启动...
环境: 生产
日志级别: INFO
默认 LLM 提供商: qwen
默认 Embedding 提供商: qwen
```

## 安全建议

1. ✅ 使用环境变量而不是硬编码
2. ✅ 不要提交 `.env` 文件到 Git
3. ✅ 生产环境使用密钥管理服务
4. ✅ 定期轮换 API Key
5. ✅ 使用最小权限原则

## 相关文档

- [CONFIGURATION.md](CONFIGURATION.md) - 详细配置指南
- [env.example.txt](env.example.txt) - 环境变量配置模板
- [README_NEW.md](README_NEW.md) - 项目文档


