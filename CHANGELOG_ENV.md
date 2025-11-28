# 环境变量配置更新说明

## 更新日期

2025-11-28

## 更新概述

将 PaperWhisperer 的所有配置项改为从环境变量中读取，符合 12-Factor App 最佳实践。

## 主要更改

### 1. 配置文件重构 (`app/config.py`)

#### 更改前
- 使用硬编码的默认值
- 配置项直接赋值，如 `qwen_api_base: str = "https://dashscope.aliyuncs.com/..."`
- 自动读取 `.env` 文件（可能导致权限问题）

#### 更改后
- **所有配置项都从环境变量读取**
- 使用 `Field(default_factory=lambda: os.getenv(...))` 模式
- 每个配置项都有清晰的描述
- `.env` 文件变为可选（由应用启动时加载）
- 移除硬编码的配置类内部 `.env` 文件读取

### 2. 应用启动文件更新 (`app/main.py`)

添加了 `.env` 文件自动加载功能：

```python
from dotenv import load_dotenv
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    try:
        load_dotenv(env_file)
    except (PermissionError, OSError):
        pass
```

### 3. 新增文档文件

1. **`env.example.txt`** - 环境变量配置模板
   - 包含所有可配置项
   - 带有详细注释
   - 可直接复制为 `.env` 文件

2. **`ENVIRONMENT_VARIABLES.md`** - 环境变量配置说明
   - 详细的配置方式说明
   - 完整的配置项列表
   - 安全最佳实践

3. **`CHANGELOG_ENV.md`** - 本更新说明文档

### 4. 文档更新

#### `CONFIGURATION.md`
- 更新了配置优先级说明
- 添加了完整的环境变量参考表（34 个配置项）
- 更详细的可选配置说明

#### `README_NEW.md`
- 更新了环境变量配置部分
- 增加了两种配置方式的说明
- 添加了文档链接

## 配置方式对比

### 之前的方式

```python
class Settings(BaseSettings):
    qwen_api_key: Optional[str] = None
    qwen_api_base: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    class Config:
        env_file = ".env"  # 强制读取，可能有权限问题
```

### 现在的方式

```python
class Settings(BaseSettings):
    qwen_api_key: Optional[str] = Field(default=None, description="通义千问 API Key")
    qwen_api_base: str = Field(
        default_factory=lambda: os.getenv("QWEN_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        description="通义千问 API Base URL"
    )
    
    model_config = {
        "case_sensitive": False,
        "extra": "ignore",
    }
```

## 配置项总览

所有配置项都支持通过环境变量设置：

| 类别 | 配置项数量 |
|------|----------|
| LLM API 配置 | 6 |
| MinerU 配置 | 4 |
| Milvus 配置 | 3 |
| 默认提供商配置 | 4 |
| 应用服务配置 | 6 |
| 路径配置 | 6 |
| 调试配置 | 2 |
| **总计** | **31** |

## 使用说明

### 开发环境

1. 复制环境变量模板：
   ```bash
   cp env.example.txt .env
   ```

2. 编辑 `.env` 文件，填写你的配置

3. 启动应用（会自动加载 `.env`）

### 生产环境

直接设置环境变量：

```bash
export QWEN_API_KEY="your-key"
export MINERU_TOKEN="your-token"
./run.sh
```

或在 Docker Compose 中：

```yaml
environment:
  - QWEN_API_KEY=${QWEN_API_KEY}
  - MINERU_TOKEN=${MINERU_TOKEN}
```

## 兼容性说明

✅ **向后兼容** - 所有现有的环境变量配置仍然有效

✅ **默认值保持不变** - 如果不设置环境变量，使用的默认值与之前相同

✅ **Docker Compose 配置无需修改** - 现有的 `docker-compose.yml` 配置仍然有效

## 优势

1. ✅ **更安全** - 敏感信息不会硬编码在代码中
2. ✅ **更灵活** - 可在不修改代码的情况下更改配置
3. ✅ **更标准** - 符合 12-Factor App 最佳实践
4. ✅ **更易部署** - 支持多种部署环境（Docker、K8s、云平台）
5. ✅ **更好的权限控制** - `.env` 文件变为可选，避免权限问题

## 测试验证

可以通过以下命令验证配置是否正确加载：

```bash
python -c "from app.config import settings; print(f'Milvus: {settings.milvus_host}:{settings.milvus_port}'); print(f'LLM: {settings.default_llm_provider}')"
```

预期输出：
```
Milvus: milvus:19530
LLM: qwen
```

## 迁移指南

如果你之前使用了 `.env` 文件：

1. ✅ 无需任何更改 - 现有的 `.env` 文件仍然会被自动加载
2. ✅ 建议：对照 `env.example.txt` 检查是否有新的配置项
3. ✅ 建议：将敏感信息移到环境变量中（生产环境）

如果你之前使用了环境变量：

1. ✅ 无需任何更改 - 所有环境变量仍然有效
2. ✅ 环境变量的优先级高于 `.env` 文件

## 相关文档

- [ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md) - 环境变量配置详细说明
- [CONFIGURATION.md](CONFIGURATION.md) - 完整配置指南
- [env.example.txt](env.example.txt) - 配置模板
- [README_NEW.md](README_NEW.md) - 项目文档

## 问题反馈

如有任何问题，请提交 Issue。


