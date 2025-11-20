"""
RAG (Retrieval-Augmented Generation) 服务
实现基于检索的对话问答
"""
from typing import List, Dict, Any, Optional, AsyncIterator
import uuid
from collections import deque

from app.models.schemas import ChatMessage, ChatHistory
from app.services.vectorization_service import vectorization_service
from app.services.llm_factory import llm_factory
from app.utils.logger import log
from app.config import settings
from datetime import datetime


class RAGService:
    """RAG 对话服务"""
    
    # 系统 Prompt
    SYSTEM_PROMPT = """你是一个专业的学术论文助手。你的任务是根据提供的论文内容回答用户的问题。

回答要求：
1. 基于提供的论文片段回答问题，不要编造信息
2. 如果论文片段中没有相关信息，请明确说明
3. 使用清晰、准确的学术语言
4. 如果问题涉及多个方面，请分点回答
5. 必要时可以引用论文原文

请始终记住：你的回答应该基于论文内容，而不是你的一般知识。"""
    
    RAG_PROMPT_TEMPLATE = """基于以下论文片段回答用户的问题。

论文相关片段：
{context}

用户问题：{question}

请基于上述论文片段给出准确、详细的回答。如果片段中没有足够信息回答问题，请说明。"""
    
    def __init__(self):
        # 会话存储（简单内存存储，生产环境应使用 Redis）
        self.sessions: Dict[str, ChatHistory] = {}
        self.max_history_length = 10  # 最大历史消息数
    
    def create_session(self, paper_id: str) -> str:
        """
        创建新的对话会话
        
        Args:
            paper_id: 论文ID
            
        Returns:
            会话ID
        """
        session_id = str(uuid.uuid4())
        
        chat_history = ChatHistory(
            session_id=session_id,
            paper_id=paper_id,
            messages=[],
            created_at=datetime.now()
        )
        
        self.sessions[session_id] = chat_history
        
        log.info(f"创建对话会话: {session_id}, 论文: {paper_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[ChatHistory]:
        """获取会话"""
        return self.sessions.get(session_id)
    
    def _format_context(self, search_results: List[Dict[str, Any]]) -> str:
        """
        格式化检索结果为上下文
        
        Args:
            search_results: 检索结果
            
        Returns:
            格式化的上下文字符串
        """
        context_parts = []
        
        for i, result in enumerate(search_results, 1):
            text = result["text"]
            section = result["metadata"].get("section_title", "未知章节")
            score = result["score"]
            
            context_parts.append(f"[片段 {i}] (章节: {section}, 相关度: {score:.3f})\n{text}\n")
        
        return "\n---\n\n".join(context_parts)
    
    def _build_messages(
        self,
        question: str,
        context: str,
        history: Optional[List[ChatMessage]] = None
    ) -> List[Dict[str, str]]:
        """
        构建对话消息列表
        
        Args:
            question: 用户问题
            context: 检索到的上下文
            history: 对话历史
            
        Returns:
            消息列表
        """
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT}
        ]
        
        # 添加历史对话（最近的几轮）
        if history:
            recent_history = history[-6:]  # 最近3轮对话
            for msg in recent_history:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # 添加当前问题和上下文
        prompt = self.RAG_PROMPT_TEMPLATE.format(
            context=context,
            question=question
        )
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        return messages
    
    async def chat(
        self,
        paper_id: str,
        question: str,
        session_id: Optional[str] = None,
        provider: Optional[str] = None,
        stream: bool = False
    ) -> tuple[str, str, List[Dict[str, Any]]]:
        """
        基于论文进行对话
        
        Args:
            paper_id: 论文ID
            question: 用户问题
            session_id: 会话ID（可选）
            provider: LLM 提供商
            stream: 是否流式输出
            
        Returns:
            (session_id, answer, sources) 元组
        """
        # 创建或获取会话
        if not session_id:
            session_id = self.create_session(paper_id)
        
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"会话不存在: {session_id}")
        
        # 检查论文ID是否匹配
        if session.paper_id != paper_id:
            raise ValueError(f"会话的论文ID ({session.paper_id}) 与请求的论文ID ({paper_id}) 不匹配")
        
        log.info(f"处理对话: session={session_id}, question={question[:50]}...")
        
        try:
            # 1. 向量检索相关内容
            search_results = await vectorization_service.search_similar_chunks(
                query_text=question,
                paper_id=paper_id,
                top_k=settings.top_k_retrieval
            )
            
            if not search_results:
                log.warning(f"未检索到相关内容: {paper_id}")
                answer = "抱歉，我在论文中没有找到与您问题相关的内容。您可以尝试换一个问法或问其他问题。"
                sources = []
            else:
                # 2. 构建上下文
                context = self._format_context(search_results)
                
                # 3. 构建消息
                messages = self._build_messages(
                    question=question,
                    context=context,
                    history=session.messages
                )
                
                # 4. 调用 LLM 生成回答
                if stream:
                    # 流式输出暂不支持（需要特殊处理）
                    answer = await llm_factory.chat(
                        messages=messages,
                        provider=provider,
                        temperature=0.7,
                        stream=False
                    )
                else:
                    answer = await llm_factory.chat(
                        messages=messages,
                        provider=provider,
                        temperature=0.7,
                        stream=False
                    )
                
                sources = search_results
            
            # 5. 保存对话历史
            user_message = ChatMessage(role="user", content=question, timestamp=datetime.now())
            assistant_message = ChatMessage(role="assistant", content=answer, timestamp=datetime.now())
            
            session.messages.append(user_message)
            session.messages.append(assistant_message)
            
            # 限制历史长度
            if len(session.messages) > self.max_history_length * 2:
                session.messages = session.messages[-(self.max_history_length * 2):]
            
            log.info(f"对话完成: session={session_id}")
            return session_id, answer, sources
            
        except Exception as e:
            log.error(f"对话处理失败: {e}")
            raise
    
    async def chat_stream(
        self,
        paper_id: str,
        question: str,
        session_id: Optional[str] = None,
        provider: Optional[str] = None
    ) -> AsyncIterator[str]:
        """
        流式对话（生成器）
        
        Args:
            paper_id: 论文ID
            question: 用户问题
            session_id: 会话ID
            provider: LLM 提供商
            
        Yields:
            回答片段
        """
        # 创建或获取会话
        if not session_id:
            session_id = self.create_session(paper_id)
        
        session = self.get_session(session_id)
        if not session or session.paper_id != paper_id:
            yield "错误：会话无效"
            return
        
        try:
            # 检索相关内容
            search_results = await vectorization_service.search_similar_chunks(
                query_text=question,
                paper_id=paper_id,
                top_k=settings.top_k_retrieval
            )
            
            if not search_results:
                yield "抱歉，我在论文中没有找到与您问题相关的内容。"
                return
            
            # 构建上下文和消息
            context = self._format_context(search_results)
            messages = self._build_messages(question, context, session.messages)
            
            # 流式生成
            response_chunks = []
            stream_generator = await llm_factory.chat(
                messages=messages,
                provider=provider,
                temperature=0.7,
                stream=True
            )
            
            async for chunk in stream_generator:
                response_chunks.append(chunk)
                yield chunk
            
            # 保存完整回答到历史
            full_answer = "".join(response_chunks)
            user_message = ChatMessage(role="user", content=question, timestamp=datetime.now())
            assistant_message = ChatMessage(role="assistant", content=full_answer, timestamp=datetime.now())
            
            session.messages.append(user_message)
            session.messages.append(assistant_message)
            
            if len(session.messages) > self.max_history_length * 2:
                session.messages = session.messages[-(self.max_history_length * 2):]
            
        except Exception as e:
            log.error(f"流式对话失败: {e}")
            yield f"错误：{str(e)}"
    
    def get_history(self, session_id: str) -> Optional[List[ChatMessage]]:
        """
        获取对话历史
        
        Args:
            session_id: 会话ID
            
        Returns:
            消息列表
        """
        session = self.get_session(session_id)
        return session.messages if session else None
    
    def clear_session(self, session_id: str):
        """清除会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            log.info(f"清除会话: {session_id}")


# 全局服务实例
rag_service = RAGService()

