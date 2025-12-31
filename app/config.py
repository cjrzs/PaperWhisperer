"""
配置管理模块
支持从环境变量和 .env 文件加载配置
.env 文件优先级高于系统环境变量
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os
from pathlib import Path
from dotenv import load_dotenv

# 在创建 Settings 实例前加载 .env 文件
# override=True 确保 .env 文件的配置优先于系统环境变量
_env_file = Path(__file__).parent.parent / ".env"
if _env_file.exists():
    load_dotenv(_env_file, override=True)


class Settings(BaseSettings):
    """应用配置 - 所有配置都从环境变量中读取"""
    
    # LLM Provider Configuration
    qwen_api_key: Optional[str] = Field(default=None, description="通义千问 API Key")
    qwen_api_base: str = Field(
        default_factory=lambda: os.getenv("QWEN_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        description="通义千问 API Base URL"
    )
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API Key")
    openai_api_base: str = Field(
        default_factory=lambda: os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
        description="OpenAI API Base URL"
    )
    deepseek_api_key: Optional[str] = Field(default=None, description="DeepSeek API Key")
    deepseek_api_base: str = Field(
        default_factory=lambda: os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1"),
        description="DeepSeek API Base URL"
    )
    
    # MinerU Configuration
    mineru_token: Optional[str] = Field(default=None, description="MinerU API Token")
    mineru_api_base: str = Field(
        default_factory=lambda: os.getenv("MINERU_API_BASE", "https://mineru.net/api/v4"),
        description="MinerU API Base URL"
    )
    mineru_poll_interval: int = Field(
        default_factory=lambda: int(os.getenv("MINERU_POLL_INTERVAL", "3")),
        description="MinerU 轮询间隔（秒）"
    )
    mineru_timeout: int = Field(
        default_factory=lambda: int(os.getenv("MINERU_TIMEOUT", "600")),
        description="MinerU 超时时间（秒）"
    )
    mineru_max_file_size: int = Field(
        default_factory=lambda: int(os.getenv("MINERU_MAX_FILE_SIZE", "10")),
        description="MinerU 直接上传文件的最大大小（MB），超过此大小建议使用 URL 方式"
    )
    
    # Milvus Configuration
    milvus_host: str = Field(
        default_factory=lambda: os.getenv("MILVUS_HOST", "milvus"),
        description="Milvus 主机地址"
    )
    milvus_port: int = Field(
        default_factory=lambda: int(os.getenv("MILVUS_PORT", "19530")),
        description="Milvus 端口"
    )
    milvus_collection_name: str = Field(
        default_factory=lambda: os.getenv("MILVUS_COLLECTION_NAME", "paper_chunks"),
        description="Milvus 集合名称"
    )
    
    # Default Providers
    default_llm_provider: str = Field(
        default_factory=lambda: os.getenv("DEFAULT_LLM_PROVIDER", "qwen"),
        description="默认 LLM 提供商"
    )
    default_llm_model: str = Field(
        default_factory=lambda: os.getenv("DEFAULT_LLM_MODEL", "qwen-max"),
        description="默认 LLM 模型"
    )
    default_embedding_provider: str = Field(
        default_factory=lambda: os.getenv("DEFAULT_EMBEDDING_PROVIDER", "qwen"),
        description="默认 Embedding 提供商"
    )
    default_embedding_model: str = Field(
        default_factory=lambda: os.getenv("DEFAULT_EMBEDDING_MODEL", "text-embedding-v3"),
        description="默认 Embedding 模型"
    )
    
    # Application Settings
    backend_port: int = Field(
        default_factory=lambda: int(os.getenv("BACKEND_PORT", "8000")),
        description="后端服务端口"
    )
    frontend_port: int = Field(
        default_factory=lambda: int(os.getenv("FRONTEND_PORT", "80")),
        description="前端服务端口"
    )
    max_upload_size: int = Field(
        default_factory=lambda: int(os.getenv("MAX_UPLOAD_SIZE", "50")),
        description="最大上传文件大小（MB）"
    )
    chunk_size: int = Field(
        default_factory=lambda: int(os.getenv("CHUNK_SIZE", "800")),
        description="文本分块大小（tokens）"
    )
    chunk_overlap: int = Field(
        default_factory=lambda: int(os.getenv("CHUNK_OVERLAP", "100")),
        description="文本分块重叠大小（tokens）"
    )
    top_k_retrieval: int = Field(
        default_factory=lambda: int(os.getenv("TOP_K_RETRIEVAL", "5")),
        description="检索返回的 Top K 结果数"
    )
    
    # Agent Configuration
    agent_max_retrieval_rounds: int = Field(
        default_factory=lambda: int(os.getenv("AGENT_MAX_RETRIEVAL_ROUNDS", "5")),
        description="Agent 最大检索轮次"
    )
    agent_intent_temperature: float = Field(
        default_factory=lambda: float(os.getenv("AGENT_INTENT_TEMPERATURE", "0.3")),
        description="Agent 意图识别温度"
    )
    agent_evaluation_temperature: float = Field(
        default_factory=lambda: float(os.getenv("AGENT_EVALUATION_TEMPERATURE", "0.2")),
        description="Agent 完备性评估温度"
    )
    
    # Paths - 基于环境变量或使用默认路径
    base_dir: Path = Field(
        default_factory=lambda: Path(os.getenv("BASE_DIR", str(Path(__file__).parent.parent))),
        description="项目根目录"
    )
    
    @property
    def data_dir(self) -> Path:
        """数据目录"""
        return Path(os.getenv("DATA_DIR", str(self.base_dir / "data")))
    
    @property
    def upload_dir(self) -> Path:
        """上传目录"""
        return Path(os.getenv("UPLOAD_DIR", str(self.data_dir / "uploads")))
    
    @property
    def parsed_dir(self) -> Path:
        """解析结果目录"""
        return Path(os.getenv("PARSED_DIR", str(self.data_dir / "parsed")))
    
    @property
    def embeddings_dir(self) -> Path:
        """向量嵌入目录"""
        return Path(os.getenv("EMBEDDINGS_DIR", str(self.data_dir / "embeddings")))
    
    @property
    def summaries_dir(self) -> Path:
        """摘要目录"""
        return Path(os.getenv("SUMMARIES_DIR", str(self.data_dir / "summaries")))
    
    # Debug
    debug: bool = Field(
        default_factory=lambda: os.getenv("DEBUG", "False").lower() in ("true", "1", "yes"),
        description="调试模式"
    )
    log_level: str = Field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO").upper(),
        description="日志级别"
    )
    
    model_config = {
        "case_sensitive": False,
        "extra": "ignore",
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 确保数据目录存在
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保所有必要的目录存在"""
        for directory in [
            self.data_dir,
            self.upload_dir,
            self.parsed_dir,
            self.embeddings_dir,
            self.summaries_dir
        ]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_llm_config(self, provider: Optional[str] = None):
        """获取 LLM 配置"""
        provider = provider or self.default_llm_provider
        
        # 转换为小写以支持大小写不敏感
        provider = provider.lower()
        
        if provider == "qwen":
            return {
                "api_key": self.qwen_api_key,
                "base_url": self.qwen_api_base,
                "model": self.default_llm_model
            }
        elif provider == "openai":
            return {
                "api_key": self.openai_api_key,
                "base_url": self.openai_api_base,
                "model": "gpt-4-turbo-preview"
            }
        elif provider == "deepseek":
            return {
                "api_key": self.deepseek_api_key,
                "base_url": self.deepseek_api_base,
                "model": "deepseek-chat"
            }
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
    
    def get_embedding_config(self, provider: Optional[str] = None):
        """获取 Embedding 配置"""
        provider = provider or self.default_embedding_provider
        
        # 转换为小写以支持大小写不敏感
        provider = provider.lower()
        
        if provider == "qwen":
            return {
                "api_key": self.qwen_api_key,
                "base_url": self.qwen_api_base,
                "model": self.default_embedding_model
            }
        elif provider == "openai":
            return {
                "api_key": self.openai_api_key,
                "base_url": self.openai_api_base,
                "model": "text-embedding-3-small"
            }
        else:
            raise ValueError(f"Unknown embedding provider: {provider}")


# 全局配置实例
# 配置优先级：.env 文件 > 系统环境变量 > 默认值
settings = Settings()

