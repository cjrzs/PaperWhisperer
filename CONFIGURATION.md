# PaperWhisperer 配置指南

## 🔑 配置优先级

系统按以下优先级读取配置：

1. **环境变量**（最高优先级，推荐用于生产环境）
2. `.env` 文件（次优先级，适合本地开发）
3. 默认值（最低优先级）

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

### 默认 LLM 提供商
```bash
export DEFAULT_LLM_PROVIDER="qwen"  # qwen, openai, deepseek
```

### 默认 Embedding 提供商
```bash
export DEFAULT_EMBEDDING_PROVIDER="qwen"  # qwen, openai
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

## 📚 更多信息

- [项目文档](README.md)
- [Docker 部署指南](docker-compose.yml)
- [API 文档](http://localhost:8000/docs)
