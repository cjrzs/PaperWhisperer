"""
配置管理模块
支持从环境变量和 .env 文件加载配置
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """应用配置"""
    
    # LLM Provider Configuration
    qwen_api_key: Optional[str] = None
    qwen_api_base: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    openai_api_key: Optional[str] = None
    openai_api_base: str = "https://api.openai.com/v1"
    deepseek_api_key: Optional[str] = None
    deepseek_api_base: str = "https://api.deepseek.com/v1"
    
    # MinerU Configuration
    mineru_token: Optional[str] = None
    mineru_api_base: str = "https://mineru.net/api/v4"
    mineru_poll_interval: int = 3  # seconds
    mineru_timeout: int = 600  # seconds
    
    # Milvus Configuration
    milvus_host: str = "milvus"
    milvus_port: int = 19530
    milvus_collection_name: str = "paper_chunks"
    
    # Default Providers
    default_llm_provider: str = "qwen"
    default_llm_model: str = "qwen-max"
    default_embedding_provider: str = "qwen"
    default_embedding_model: str = "text-embedding-v3"
    
    # Application Settings
    backend_port: int = 8000
    frontend_port: int = 80
    max_upload_size: int = 50  # MB
    chunk_size: int = 800  # tokens
    chunk_overlap: int = 100  # tokens
    top_k_retrieval: int = 5
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent
    data_dir: Path = base_dir / "data"
    upload_dir: Path = data_dir / "uploads"
    parsed_dir: Path = data_dir / "parsed"
    embeddings_dir: Path = data_dir / "embeddings"
    summaries_dir: Path = data_dir / "summaries"
    
    # Debug
    debug: bool = False
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        # 环境变量优先级高于 .env 文件（pydantic 默认行为）
        # 即使 .env 文件存在，环境变量的值也会覆盖 .env 中的值
    
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
settings = Settings()

