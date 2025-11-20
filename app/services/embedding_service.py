"""
Embedding 服务
支持多个 Embedding 提供商
"""
from typing import List, Optional
from openai import AsyncOpenAI

from app.config import settings
from app.utils.logger import log
from app.utils.async_helper import async_retry


class EmbeddingService:
    """Embedding 服务类"""
    
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        """
        初始化 Embedding 服务
        
        Args:
            provider: 提供商名称
            model: 模型名称
        """
        self.provider = provider or settings.default_embedding_provider
        self.config = settings.get_embedding_config(self.provider)
        self.model = model or self.config["model"]
        
        if not self.config["api_key"]:
            raise ValueError(f"{self.provider} API Key 未配置")
        
        self.client = AsyncOpenAI(
            api_key=self.config["api_key"],
            base_url=self.config["base_url"]
        )
        
        log.info(f"初始化 Embedding 服务: {self.provider}, 模型: {self.model}")
    
    @async_retry(max_retries=3, delay=1.0)
    async def embed_text(self, text: str) -> List[float]:
        """
        生成单个文本的 embedding
        
        Args:
            text: 输入文本
            
        Returns:
            Embedding 向量
        """
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=text
            )
            
            embedding = response.data[0].embedding
            log.debug(f"生成 embedding: 维度={len(embedding)}")
            return embedding
            
        except Exception as e:
            log.error(f"生成 embedding 失败: {e}")
            raise
    
    @async_retry(max_retries=3, delay=1.0)
    async def embed_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """
        批量生成 embedding
        
        Args:
            texts: 文本列表
            batch_size: 批次大小
            
        Returns:
            Embedding 向量列表
        """
        if not texts:
            return []
        
        all_embeddings = []
        
        # 分批处理
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=batch
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
                log.debug(f"批量生成 embedding: {i+1}-{i+len(batch)}/{len(texts)}")
                
            except Exception as e:
                log.error(f"批量生成 embedding 失败 (批次 {i//batch_size + 1}): {e}")
                raise
        
        log.info(f"批量 embedding 完成: 总数={len(all_embeddings)}, 维度={len(all_embeddings[0])}")
        return all_embeddings
    
    def get_dimension(self) -> int:
        """
        获取 embedding 维度
        
        Returns:
            维度数
        """
        # 不同模型的维度（可以根据需要扩展）
        dimension_map = {
            "text-embedding-v3": 1024,  # Qwen
            "text-embedding-3-small": 1536,  # OpenAI
            "text-embedding-3-large": 3072,  # OpenAI
        }
        
        # 尝试匹配模型名
        for model_prefix, dim in dimension_map.items():
            if model_prefix in self.model:
                return dim
        
        # 默认维度
        return 1536


# 创建全局服务实例的工厂函数
def create_embedding_service(
    provider: Optional[str] = None,
    model: Optional[str] = None
) -> EmbeddingService:
    """
    创建 Embedding 服务实例
    
    Args:
        provider: 提供商名称
        model: 模型名称
        
    Returns:
        EmbeddingService 实例
    """
    return EmbeddingService(provider=provider, model=model)

