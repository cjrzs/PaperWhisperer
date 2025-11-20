"""
摘要路由
处理论文摘要生成
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional

from app.models.schemas import SummaryRequest, PaperSummary, TaskStatus, LLMProvider, PaperStructure, PaperSection, PaperMetadata
from app.services.summarizer import summarizer_service
from app.utils.file_manager import FileManager
from app.utils.logger import log

router = APIRouter()

# 摘要任务状态
summary_tasks = {}


async def generate_summary_background(
    task_id: str,
    paper_id: str,
    summary_type: str,
    provider: Optional[str]
):
    """后台摘要生成任务"""
    try:
        summary_tasks[task_id] = {
            "status": TaskStatus.PROCESSING,
            "progress": 0
        }
        
        # 加载论文
        paper_data = await FileManager.load_parsed_content(paper_id)
        if not paper_data:
            raise ValueError(f"论文不存在: {paper_id}")
        
        # 重建 PaperStructure
        metadata = PaperMetadata(**paper_data["metadata"])
        sections = [PaperSection(**s) for s in paper_data["sections"]]
        paper = PaperStructure(
            paper_id=paper_id,
            metadata=metadata,
            sections=sections,
            full_content=paper_data["full_content"]
        )
        
        # 生成摘要
        result = await summarizer_service.summarize_paper(
            paper=paper,
            provider=provider,
            summary_type=summary_type
        )
        
        # 保存摘要
        await FileManager.save_summary(
            paper_id,
            result.dict()
        )
        
        summary_tasks[task_id] = {
            "status": TaskStatus.COMPLETED,
            "progress": 100
        }
        
        log.info(f"摘要生成完成: task_id={task_id}, paper_id={paper_id}")
        
    except Exception as e:
        log.error(f"摘要生成失败: task_id={task_id}, error={e}")
        summary_tasks[task_id] = {
            "status": TaskStatus.FAILED,
            "progress": 0,
            "error": str(e)
        }


@router.post("/summary/{paper_id}")
async def generate_summary(
    paper_id: str,
    background_tasks: BackgroundTasks,
    summary_type: str = "comprehensive",
    provider: Optional[LLMProvider] = None
):
    """
    生成论文摘要
    """
    # 检查论文是否存在
    paper_data = await FileManager.load_parsed_content(paper_id)
    if not paper_data:
        raise HTTPException(status_code=404, detail="论文不存在")
    
    # 检查是否已有摘要
    existing_summary = await FileManager.load_summary(paper_id)
    if existing_summary:
        return {
            "task_id": paper_id,
            "status": "completed",
            "message": "该论文已有摘要结果"
        }
    
    # 创建摘要任务
    task_id = f"{paper_id}_summary"
    
    summary_tasks[task_id] = {
        "status": TaskStatus.PENDING,
        "progress": 0
    }
    
    # 后台生成
    background_tasks.add_task(
        generate_summary_background,
        task_id=task_id,
        paper_id=paper_id,
        summary_type=summary_type,
        provider=provider.value if provider else None
    )
    
    return {
        "task_id": task_id,
        "status": "processing",
        "message": "摘要生成任务已创建"
    }


@router.get("/summary/{paper_id}")
async def get_summary(paper_id: str):
    """
    获取论文摘要
    """
    result = await FileManager.load_summary(paper_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="摘要不存在")
    
    return result

