"""
上传与解析路由
处理 PDF 上传和论文解析
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import Optional
import asyncio

from app.models.schemas import UploadResponse, ParseStatusResponse, TaskStatus, PaperMetadata
from app.services.mineru_client import mineru_client
from app.services.paper_parser import paper_parser
from app.services.vectorization_service import vectorization_service
from app.utils.file_manager import FileManager
from app.utils.logger import log
from app.config import settings

router = APIRouter()

# 任务状态存储（简单实现，生产环境应使用 Redis）
task_status = {}


async def process_paper_background(task_id: str, file_id: str, file_path, is_url: bool = False):
    """后台任务：处理论文"""
    try:
        task_status[task_id] = {
            "status": TaskStatus.PROCESSING,
            "progress": 10,
            "paper_id": None,
            "metadata": None,
            "error": None
        }
        
        # 1. 调用 MinerU 解析
        log.info(f"开始解析论文: task_id={task_id}")
        
        if is_url:
            mineru_result = await mineru_client.parse_pdf(url=file_path, paper_id=file_id)
        else:
            mineru_result = await mineru_client.parse_pdf(file_path=file_path, paper_id=file_id)
        
        task_status[task_id]["progress"] = 50
        
        # 2. 解析论文结构
        paper_structure = paper_parser.parse_result(file_id, mineru_result)
        
        # 3. 保存解析内容
        await FileManager.save_parsed_content(
            file_id,
            {
                "metadata": paper_structure.metadata.dict(),
                "sections": [s.dict() for s in paper_structure.sections],
                "full_content": paper_structure.full_content
            }
        )
        
        task_status[task_id]["progress"] = 70
        
        # 4. 向量化并存储
        log.info(f"开始向量化论文: {file_id}")
        await vectorization_service.vectorize_and_store_paper(paper_structure)
        
        task_status[task_id]["progress"] = 100
        task_status[task_id]["status"] = TaskStatus.COMPLETED
        task_status[task_id]["paper_id"] = file_id
        task_status[task_id]["metadata"] = paper_structure.metadata.dict()
        
        log.info(f"论文处理完成: task_id={task_id}, paper_id={file_id}")
        
    except Exception as e:
        log.error(f"论文处理失败: task_id={task_id}, error={e}")
        task_status[task_id]["status"] = TaskStatus.FAILED
        task_status[task_id]["error"] = str(e)


@router.post("/upload", response_model=UploadResponse)
async def upload_paper(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    上传 PDF 文件并解析
    """
    # 检查文件类型
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="只支持 PDF 文件")
    
    # 读取文件内容
    content = await file.read()
    
    # 检查文件大小
    if not FileManager.check_file_size(len(content)):
        raise HTTPException(
            status_code=413,
            detail=f"文件太大，最大支持 {settings.max_upload_size}MB"
        )
    
    # 保存文件
    file_id, file_path = await FileManager.save_upload_file(content, file.filename)
    
    # 创建任务
    task_id = file_id
    task_status[task_id] = {
        "status": TaskStatus.PENDING,
        "progress": 0,
        "paper_id": None,
        "metadata": None,
        "error": None
    }
    
    # 后台处理
    background_tasks.add_task(
        process_paper_background,
        task_id=task_id,
        file_id=file_id,
        file_path=file_path,
        is_url=False
    )
    
    log.info(f"文件上传成功: {file.filename}, task_id={task_id}")
    
    return UploadResponse(
        task_id=task_id,
        status=TaskStatus.PENDING,
        message="文件上传成功，正在解析中..."
    )


@router.post("/parse_url", response_model=UploadResponse)
async def parse_url(
    background_tasks: BackgroundTasks,
    url: str
):
    """
    通过 URL 解析论文（如 arXiv 链接）
    """
    import hashlib
    
    # 生成任务ID
    task_id = hashlib.md5(url.encode()).hexdigest()
    
    # 检查是否已经在处理
    if task_id in task_status and task_status[task_id]["status"] == TaskStatus.PROCESSING:
        return UploadResponse(
            task_id=task_id,
            status=TaskStatus.PROCESSING,
            message="该论文正在解析中..."
        )
    
    # 创建任务
    task_status[task_id] = {
        "status": TaskStatus.PENDING,
        "progress": 0,
        "paper_id": None,
        "metadata": None,
        "error": None
    }
    
    # 后台处理
    background_tasks.add_task(
        process_paper_background,
        task_id=task_id,
        file_id=task_id,
        file_path=url,
        is_url=True
    )
    
    log.info(f"URL 解析任务创建: url={url}, task_id={task_id}")
    
    return UploadResponse(
        task_id=task_id,
        status=TaskStatus.PENDING,
        message="解析任务已创建..."
    )


@router.get("/parse_status/{task_id}", response_model=ParseStatusResponse)
async def get_parse_status(task_id: str):
    """
    查询解析状态
    """
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    status_info = task_status[task_id]
    
    return ParseStatusResponse(
        task_id=task_id,
        status=status_info["status"],
        progress=status_info["progress"],
        paper_id=status_info["paper_id"],
        metadata=status_info["metadata"],
        error=status_info["error"]
    )


@router.get("/paper/{paper_id}")
async def get_paper(paper_id: str):
    """
    获取论文详情
    """
    paper_data = await FileManager.load_parsed_content(paper_id)
    
    if not paper_data:
        raise HTTPException(status_code=404, detail="论文不存在")
    
    return paper_data


@router.get("/papers/list")
async def list_papers():
    """
    获取所有已解析的论文列表
    """
    papers = []
    parsed_dir = settings.parsed_dir
    
    # 遍历所有解析后的JSON文件
    for json_file in parsed_dir.glob("*.json"):
        try:
            paper_data = await FileManager.load_parsed_content(json_file.stem)
            if paper_data and "metadata" in paper_data:
                metadata = paper_data["metadata"]
                papers.append({
                    "paper_id": json_file.stem,
                    "title": metadata.get("title", "未知标题"),
                    "authors": metadata.get("authors", []),
                    "abstract": metadata.get("abstract", ""),
                    "created_at": json_file.stat().st_ctime,
                    "modified_at": json_file.stat().st_mtime
                })
        except Exception as e:
            log.error(f"加载论文失败: {json_file}, error={e}")
            continue
    
    # 按修改时间倒序排序
    papers.sort(key=lambda x: x["modified_at"], reverse=True)
    
    return {
        "total": len(papers),
        "papers": papers
    }


@router.delete("/paper/{paper_id}")
async def delete_paper(paper_id: str):
    """
    删除论文
    """
    # 删除向量数据
    count = await vectorization_service.delete_paper_vectors(paper_id)
    
    log.info(f"删除论文: {paper_id}, 向量数: {count}")
    
    return {
        "message": "论文删除成功",
        "paper_id": paper_id,
        "vectors_deleted": count
    }

