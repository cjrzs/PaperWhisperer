"""
翻译路由
处理论文翻译请求
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional

from app.models.schemas import TranslationRequest, TranslationResult, TaskStatus, LLMProvider
from app.services.translator import translation_service
from app.services.paper_parser import paper_parser
from app.models.schemas import PaperStructure, PaperSection, PaperMetadata
from app.utils.file_manager import FileManager
from app.utils.logger import log

router = APIRouter()

# 翻译任务状态
translation_tasks = {}


async def translate_paper_background(
    task_id: str,
    paper_id: str,
    source_lang: str,
    target_lang: str,
    provider: Optional[str]
):
    """后台翻译任务"""
    try:
        translation_tasks[task_id] = {
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
        
        # 翻译
        result = await translation_service.translate_paper(
            paper=paper,
            source_lang=source_lang,
            target_lang=target_lang,
            provider=provider
        )
        
        # 保存翻译结果
        await FileManager.save_translation(
            paper_id,
            result.dict()
        )
        
        translation_tasks[task_id] = {
            "status": TaskStatus.COMPLETED,
            "progress": 100
        }
        
        log.info(f"翻译完成: task_id={task_id}, paper_id={paper_id}")
        
    except Exception as e:
        log.error(f"翻译失败: task_id={task_id}, error={e}")
        translation_tasks[task_id] = {
            "status": TaskStatus.FAILED,
            "progress": 0,
            "error": str(e)
        }


@router.post("/translate/{paper_id}")
async def translate_paper(
    paper_id: str,
    background_tasks: BackgroundTasks,
    source_lang: str = "英文",
    target_lang: str = "中文",
    provider: Optional[LLMProvider] = None
):
    """
    翻译论文
    """
    # 检查论文是否存在
    paper_data = await FileManager.load_parsed_content(paper_id)
    if not paper_data:
        raise HTTPException(status_code=404, detail="论文不存在")
    
    # 检查是否已有翻译
    existing_translation = await FileManager.load_translation(paper_id)
    if existing_translation:
        return {
            "task_id": paper_id,
            "status": "completed",
            "message": "该论文已有翻译结果"
        }
    
    # 创建翻译任务
    task_id = f"{paper_id}_translation"
    
    translation_tasks[task_id] = {
        "status": TaskStatus.PENDING,
        "progress": 0
    }
    
    # 后台翻译
    background_tasks.add_task(
        translate_paper_background,
        task_id=task_id,
        paper_id=paper_id,
        source_lang=source_lang,
        target_lang=target_lang,
        provider=provider.value if provider else None
    )
    
    return {
        "task_id": task_id,
        "status": "processing",
        "message": "翻译任务已创建"
    }


@router.get("/translate/status/{task_id}")
async def get_translation_status(task_id: str):
    """
    查询翻译状态
    """
    if task_id not in translation_tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return translation_tasks[task_id]


@router.get("/translate/result/{paper_id}")
async def get_translation_result(paper_id: str):
    """
    获取翻译结果
    """
    result = await FileManager.load_translation(paper_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="翻译结果不存在")
    
    return result

