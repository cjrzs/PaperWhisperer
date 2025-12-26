"""
LLM 工厂模式
支持多个 LLM 提供商的统一接口
"""
from typing import List, Dict, Any, Optional, AsyncIterator
from openai import AsyncOpenAI
from abc import ABC, abstractmethod

from app.config import settings
from app.utils.logger import log


class BaseLLMProvider(ABC):
    """LLM 提供商基类"""
    
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
    
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Any:
        """生成对话补全"""
        pass
    
    async def _create_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
        stream: bool
    ):
        """内部方法：调用 OpenAI 兼容 API"""
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "stream": stream
            }
            
            if max_tokens:
                kwargs["max_tokens"] = max_tokens
            
            response = await self.client.chat.completions.create(**kwargs)
            return response
            
        except Exception as e:
            log.error(f"LLM API 调用失败 ({self.__class__.__name__}): {e}")
            raise


class QwenProvider(BaseLLMProvider):
    """Qwen 提供商"""
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ):
        """Qwen 对话补全"""
        log.debug(f"调用 Qwen API: model={self.model}, stream={stream}")
        
        response = await self._create_completion(messages, temperature, max_tokens, stream)
        
        if stream:
            return self._stream_response(response)
        else:
            return response.choices[0].message.content
    
    async def _stream_response(self, response) -> AsyncIterator[str]:
        """处理流式响应"""
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class OpenAIProvider(BaseLLMProvider):
    """OpenAI 提供商"""
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ):
        """OpenAI 对话补全"""
        log.debug(f"调用 OpenAI API: model={self.model}, stream={stream}")
        
        response = await self._create_completion(messages, temperature, max_tokens, stream)
        
        if stream:
            return self._stream_response(response)
        else:
            return response.choices[0].message.content
    
    async def _stream_response(self, response) -> AsyncIterator[str]:
        """处理流式响应"""
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek 提供商"""
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ):
        """DeepSeek 对话补全"""
        log.debug(f"调用 DeepSeek API: model={self.model}, stream={stream}")
        
        response = await self._create_completion(messages, temperature, max_tokens, stream)
        
        if stream:
            return self._stream_response(response)
        else:
            return response.choices[0].message.content
    
    async def _stream_response(self, response) -> AsyncIterator[str]:
        """处理流式响应"""
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class LLMFactory:
    """LLM 工厂类"""
    
    _providers = {
        "qwen": QwenProvider,
        "openai": OpenAIProvider,
        "deepseek": DeepSeekProvider
    }
    
    @classmethod
    def create(cls, provider: Optional[str] = None, model: Optional[str] = None) -> BaseLLMProvider:
        """
        创建 LLM 提供商实例
        
        Args:
            provider: 提供商名称（qwen/openai/deepseek）
            model: 模型名称
            
        Returns:
            LLM 提供商实例
        """
        provider = provider or settings.default_llm_provider
        
        # 转换为小写以支持大小写不敏感
        provider = provider.lower()
        
        if provider not in cls._providers:
            raise ValueError(f"不支持的 LLM 提供商: {provider}")
        
        # 获取配置
        config = settings.get_llm_config(provider)
        
        if not config["api_key"]:
            raise ValueError(f"{provider} API Key 未配置")
        
        # 使用指定模型或默认模型
        model_name = model or config["model"]
        
        provider_class = cls._providers[provider]
        instance = provider_class(
            api_key=config["api_key"],
            base_url=config["base_url"],
            model=model_name
        )
        
        log.info(f"创建 LLM 提供商: {provider}, 模型: {model_name}")
        return instance
    
    @classmethod
    async def chat(
        cls,
        messages: List[Dict[str, str]],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ):
        """
        便捷方法：直接进行对话
        
        Args:
            messages: 消息列表
            provider: 提供商名称
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大 token 数
            stream: 是否流式输出
            
        Returns:
            对话结果（字符串或异步生成器）
        """
        llm = cls.create(provider=provider, model=model)
        return await llm.chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )


# 全局工厂实例
llm_factory = LLMFactory()

