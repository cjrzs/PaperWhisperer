"""
配置管理模块
支持从环境变量和 .env 文件加载配置
所有配置项都从环境变量中读取
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os
from pathlib import Path


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
# 所有配置都从环境变量中读取
# 如果需要使用 .env 文件，请手动使用 python-dotenv 加载：
#   from dotenv import load_dotenv
#   load_dotenv()
settings = Settings()

