"""
对话路由
处理基于论文的对话问答
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional
import json

from app.models.schemas import ChatRequest, ChatResponse, ChatMessage, LLMProvider
from app.services.rag_service import rag_service
from app.utils.logger import log
from datetime import datetime

router = APIRouter()


@router.post("/chat/{paper_id}", response_model=ChatResponse)
async def chat_with_paper(
    paper_id: str,
    request: ChatRequest
):
    """
    与论文对话（非流式）
    """
    try:
        session_id, answer, sources = await rag_service.chat(
            paper_id=paper_id,
            question=request.message,
            session_id=request.session_id,
            provider=request.provider.value if request.provider else None,
            stream=False
        )
        
        response = ChatResponse(
            session_id=session_id,
            message=ChatMessage(
                role="assistant",
                content=answer,
                timestamp=datetime.now()
            ),
            sources=sources
        )
        
        return response
        
    except Exception as e:
        log.error(f"对话失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream/{paper_id}")
async def chat_with_paper_stream(
    paper_id: str,
    request: ChatRequest
):
    """
    与论文对话（流式）
    """
    async def generate():
        """流式生成器"""
        try:
            async for chunk in rag_service.chat_stream(
                paper_id=paper_id,
                question=request.message,
                session_id=request.session_id,
                provider=request.provider.value if request.provider else None
            ):
                # 每个 chunk 以 Server-Sent Events 格式发送
                yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
            
            # 发送结束信号
            yield f"data: {json.dumps({'done': True}, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            log.error(f"流式对话失败: {e}")
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """
    获取对话历史
    """
    history = rag_service.get_history(session_id)
    
    if history is None:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    return {
        "session_id": session_id,
        "messages": history
    }


@router.delete("/chat/session/{session_id}")
async def delete_session(session_id: str):
    """
    删除会话
    """
    rag_service.clear_session(session_id)
    
    return {
        "message": "会话已删除",
        "session_id": session_id
    }


@router.post("/chat/new_session/{paper_id}")
async def create_new_session(paper_id: str):
    """
    创建新的对话会话
    """
    session_id = rag_service.create_session(paper_id)
    
    return {
        "session_id": session_id,
        "paper_id": paper_id,
        "message": "会话创建成功"
    }

