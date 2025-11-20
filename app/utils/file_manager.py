"""
文件管理工具
处理文件上传、保存、读取等操作
"""
import aiofiles
import hashlib
import uuid
from pathlib import Path
from typing import Optional
from datetime import datetime
import json

from app.config import settings
from app.utils.logger import log


class FileManager:
    """文件管理器"""
    
    @staticmethod
    def generate_file_id(filename: str) -> str:
        """生成唯一的文件ID"""
        timestamp = datetime.now().isoformat()
        unique_str = f"{filename}{timestamp}{uuid.uuid4()}"
        return hashlib.md5(unique_str.encode()).hexdigest()
    
    @staticmethod
    async def save_upload_file(file_content: bytes, original_filename: str) -> tuple[str, Path]:
        """
        保存上传的文件
        
        Args:
            file_content: 文件内容
            original_filename: 原始文件名
            
        Returns:
            (file_id, file_path)
        """
        file_id = FileManager.generate_file_id(original_filename)
        
        # 保留原始扩展名
        extension = Path(original_filename).suffix
        filename = f"{file_id}{extension}"
        file_path = settings.upload_dir / filename
        
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
            
            log.info(f"文件保存成功: {filename}")
            return file_id, file_path
            
        except Exception as e:
            log.error(f"保存文件失败: {e}")
            raise
    
    @staticmethod
    async def save_parsed_content(paper_id: str, content: dict) -> Path:
        """
        保存解析后的内容
        
        Args:
            paper_id: 论文ID
            content: 解析后的内容（字典）
            
        Returns:
            保存的文件路径
        """
        file_path = settings.parsed_dir / f"{paper_id}.json"
        
        try:
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(content, ensure_ascii=False, indent=2))
            
            log.info(f"解析内容保存成功: {paper_id}")
            return file_path
            
        except Exception as e:
            log.error(f"保存解析内容失败: {e}")
            raise
    
    @staticmethod
    async def load_parsed_content(paper_id: str) -> Optional[dict]:
        """
        加载解析后的内容
        
        Args:
            paper_id: 论文ID
            
        Returns:
            解析后的内容或 None
        """
        file_path = settings.parsed_dir / f"{paper_id}.json"
        
        if not file_path.exists():
            log.warning(f"解析内容不存在: {paper_id}")
            return None
        
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
                
        except Exception as e:
            log.error(f"加载解析内容失败: {e}")
            return None
    
    @staticmethod
    async def save_translation(paper_id: str, translation: dict) -> Path:
        """保存翻译结果"""
        file_path = settings.summaries_dir / f"{paper_id}_translation.json"
        
        try:
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(translation, ensure_ascii=False, indent=2))
            
            log.info(f"翻译结果保存成功: {paper_id}")
            return file_path
            
        except Exception as e:
            log.error(f"保存翻译结果失败: {e}")
            raise
    
    @staticmethod
    async def load_translation(paper_id: str) -> Optional[dict]:
        """加载翻译结果"""
        file_path = settings.summaries_dir / f"{paper_id}_translation.json"
        
        if not file_path.exists():
            return None
        
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
                
        except Exception as e:
            log.error(f"加载翻译结果失败: {e}")
            return None
    
    @staticmethod
    async def save_summary(paper_id: str, summary: dict) -> Path:
        """保存摘要结果"""
        file_path = settings.summaries_dir / f"{paper_id}_summary.json"
        
        try:
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(summary, ensure_ascii=False, indent=2))
            
            log.info(f"摘要保存成功: {paper_id}")
            return file_path
            
        except Exception as e:
            log.error(f"保存摘要失败: {e}")
            raise
    
    @staticmethod
    async def load_summary(paper_id: str) -> Optional[dict]:
        """加载摘要结果"""
        file_path = settings.summaries_dir / f"{paper_id}_summary.json"
        
        if not file_path.exists():
            return None
        
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
                
        except Exception as e:
            log.error(f"加载摘要失败: {e}")
            return None
    
    @staticmethod
    def get_file_size(file_path: Path) -> int:
        """获取文件大小（字节）"""
        return file_path.stat().st_size if file_path.exists() else 0
    
    @staticmethod
    def check_file_size(file_size: int, max_size_mb: Optional[int] = None) -> bool:
        """检查文件大小是否符合限制"""
        max_size = (max_size_mb or settings.max_upload_size) * 1024 * 1024
        return file_size <= max_size

