"""
MinerU API 客户端
用于调用 MinerU 在线服务解析 PDF
"""
import asyncio
import httpx
from typing import Optional, Dict, Any
from pathlib import Path

from app.config import settings
from app.utils.logger import log
from app.utils.async_helper import async_retry


class MinerUClient:
    """MinerU API 客户端"""
    
    def __init__(self):
        self.base_url = settings.mineru_api_base
        self.token = settings.mineru_token
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        self.timeout = settings.mineru_timeout
        self.poll_interval = settings.mineru_poll_interval
    
    @async_retry(max_retries=3, delay=2.0)
    async def submit_task(self, url: Optional[str] = None, file_path: Optional[Path] = None) -> str:
        """
        提交解析任务
        
        Args:
            url: 论文 URL（如 arXiv 链接）
            file_path: 本地 PDF 文件路径
            
        Returns:
            task_id
        """
        if not url and not file_path:
            raise ValueError("必须提供 url 或 file_path 之一")
        
        if url and file_path:
            raise ValueError("url 和 file_path 只能提供其中一个")
        
        endpoint = f"{self.base_url}/extract/task"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if url:
                    # 使用 URL 提交
                    data = {
                        "url": url,
                        "model_version": "vlm"
                    }
                    response = await client.post(endpoint, headers=self.headers, json=data)
                else:
                    # 使用文件上传
                    with open(file_path, 'rb') as f:
                        files = {'file': (file_path.name, f, 'application/pdf')}
                        # 文件上传需要不同的 header
                        upload_headers = {"Authorization": f"Bearer {self.token}"}
                        response = await client.post(
                            endpoint,
                            headers=upload_headers,
                            files=files,
                            data={"model_version": "vlm"}
                        )
                
                response.raise_for_status()
                result = response.json()
                
                if result.get("code") != 200:
                    raise Exception(f"MinerU API 错误: {result.get('message')}")
                
                task_id = result.get("data")
                log.info(f"MinerU 任务提交成功: task_id={task_id}")
                return task_id
                
        except httpx.HTTPError as e:
            log.error(f"提交 MinerU 任务失败: {e}")
            raise
        except Exception as e:
            log.error(f"提交 MinerU 任务异常: {e}")
            raise
    
    @async_retry(max_retries=2, delay=1.0)
    async def check_status(self, task_id: str) -> Dict[str, Any]:
        """
        查询任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态信息
        """
        endpoint = f"{self.base_url}/extract/task/{task_id}"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(endpoint, headers=self.headers)
                response.raise_for_status()
                result = response.json()
                
                if result.get("code") != 200:
                    raise Exception(f"MinerU API 错误: {result.get('message')}")
                
                data = result.get("data", {})
                return {
                    "status": data.get("status"),  # pending, processing, completed, failed
                    "progress": data.get("progress", 0),
                    "result_url": data.get("result_url"),
                    "error": data.get("error")
                }
                
        except httpx.HTTPError as e:
            log.error(f"查询 MinerU 任务状态失败: {e}")
            raise
        except Exception as e:
            log.error(f"查询 MinerU 任务状态异常: {e}")
            raise
    
    async def wait_for_completion(self, task_id: str) -> Dict[str, Any]:
        """
        等待任务完成
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务结果
        """
        start_time = asyncio.get_event_loop().time()
        
        while True:
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > self.timeout:
                raise TimeoutError(f"MinerU 任务超时 (>{self.timeout}s): {task_id}")
            
            status_info = await self.check_status(task_id)
            status = status_info["status"]
            
            log.info(f"MinerU 任务状态: {task_id} - {status} ({status_info.get('progress', 0)}%)")
            
            if status == "completed":
                result_url = status_info.get("result_url")
                if not result_url:
                    raise Exception("任务完成但未返回结果 URL")
                
                # 下载结果
                result_content = await self._download_result(result_url)
                return result_content
            
            elif status == "failed":
                error = status_info.get("error", "未知错误")
                raise Exception(f"MinerU 任务失败: {error}")
            
            # 继续等待
            await asyncio.sleep(self.poll_interval)
    
    @async_retry(max_retries=3, delay=2.0)
    async def _download_result(self, result_url: str) -> Dict[str, Any]:
        """
        下载解析结果
        
        Args:
            result_url: 结果 URL
            
        Returns:
            解析结果（Markdown 等）
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(result_url)
                response.raise_for_status()
                
                # 根据内容类型处理
                content_type = response.headers.get("content-type", "")
                
                if "application/json" in content_type:
                    return response.json()
                elif "text/markdown" in content_type or "text/plain" in content_type:
                    return {
                        "content": response.text,
                        "format": "markdown"
                    }
                else:
                    # 尝试作为文本处理
                    return {
                        "content": response.text,
                        "format": "text"
                    }
                    
        except httpx.HTTPError as e:
            log.error(f"下载 MinerU 结果失败: {e}")
            raise
        except Exception as e:
            log.error(f"下载 MinerU 结果异常: {e}")
            raise
    
    async def parse_pdf(self, url: Optional[str] = None, file_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        完整的 PDF 解析流程（提交 -> 等待 -> 获取结果）
        
        Args:
            url: 论文 URL
            file_path: 本地文件路径
            
        Returns:
            解析结果
        """
        log.info(f"开始解析 PDF: url={url}, file={file_path}")
        
        # 提交任务
        task_id = await self.submit_task(url=url, file_path=file_path)
        
        # 等待完成
        result = await self.wait_for_completion(task_id)
        
        log.info(f"PDF 解析完成: task_id={task_id}")
        return result


# 全局客户端实例
mineru_client = MinerUClient()

