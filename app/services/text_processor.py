"""
文本处理服务
包括文本分块、清洗等功能
"""
from typing import List, Dict, Any, Optional
import tiktoken
import re

from app.config import settings
from app.utils.logger import log
from app.models.schemas import PaperStructure, TextChunk


class TextProcessor:
    """文本处理器"""
    
    def __init__(self):
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
        
        # 初始化 tokenizer（使用 cl100k_base 编码，适用于大多数模型）
        try:
            self.encoding = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            log.warning(f"加载 tokenizer 失败，使用近似计数: {e}")
            self.encoding = None
    
    def count_tokens(self, text: str) -> int:
        """
        计算文本的 token 数量
        
        Args:
            text: 输入文本
            
        Returns:
            Token 数量
        """
        if self.encoding:
            return len(self.encoding.encode(text))
        else:
            # 粗略估计：中文约1字1token，英文约4字1token
            chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
            other_chars = len(text) - chinese_chars
            return chinese_chars + other_chars // 4
    
    def clean_text(self, text: str) -> str:
        """
        清洗文本
        
        Args:
            text: 输入文本
            
        Returns:
            清洗后的文本
        """
        # 移除多余空行
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # 移除页眉页脚常见模式
        text = re.sub(r'Page \d+ of \d+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\d+\s*/\s*\d+', '', text)
        
        # 移除多余空格
        text = re.sub(r' +', ' ', text)
        
        # 去除首尾空白
        text = text.strip()
        
        return text
    
    def split_text_by_tokens(
        self,
        text: str,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None
    ) -> List[str]:
        """
        按 token 数量分割文本
        
        Args:
            text: 输入文本
            chunk_size: 块大小（tokens）
            chunk_overlap: 重叠大小（tokens）
            
        Returns:
            文本块列表
        """
        chunk_size = chunk_size or self.chunk_size
        chunk_overlap = chunk_overlap or self.chunk_overlap
        
        if not text:
            return []
        
        # 按段落分割
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            para_tokens = self.count_tokens(para)
            
            # 如果单个段落超过 chunk_size，需要进一步分割
            if para_tokens > chunk_size:
                # 保存当前 chunk
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                    current_chunk = []
                    current_tokens = 0
                
                # 分割长段落
                sub_chunks = self._split_long_paragraph(para, chunk_size)
                chunks.extend(sub_chunks)
                continue
            
            # 检查是否超过 chunk_size
            if current_tokens + para_tokens > chunk_size and current_chunk:
                # 保存当前 chunk
                chunks.append('\n\n'.join(current_chunk))
                
                # 保留 overlap
                overlap_chunk = self._get_overlap_text(current_chunk, chunk_overlap)
                current_chunk = overlap_chunk
                current_tokens = sum(self.count_tokens(p) for p in current_chunk)
            
            # 添加段落
            current_chunk.append(para)
            current_tokens += para_tokens
        
        # 保存最后一个 chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        log.debug(f"文本分块完成: 总 tokens={self.count_tokens(text)}, 块数={len(chunks)}")
        return chunks
    
    def _split_long_paragraph(self, paragraph: str, chunk_size: int) -> List[str]:
        """分割长段落"""
        # 按句子分割（简单实现）
        sentences = re.split(r'([。！？.!?]+)', paragraph)
        
        chunks = []
        current_chunk = ""
        
        for i in range(0, len(sentences), 2):
            sentence = sentences[i]
            if i + 1 < len(sentences):
                sentence += sentences[i + 1]  # 加上标点
            
            if not sentence.strip():
                continue
            
            sentence_tokens = self.count_tokens(sentence)
            current_tokens = self.count_tokens(current_chunk)
            
            if current_tokens + sentence_tokens > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += sentence
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _get_overlap_text(self, chunks: List[str], overlap_tokens: int) -> List[str]:
        """获取重叠文本"""
        overlap_chunk = []
        tokens = 0
        
        for chunk in reversed(chunks):
            chunk_tokens = self.count_tokens(chunk)
            if tokens + chunk_tokens <= overlap_tokens:
                overlap_chunk.insert(0, chunk)
                tokens += chunk_tokens
            else:
                break
        
        return overlap_chunk
    
    def create_chunks_from_paper(
        self,
        paper: PaperStructure,
        preserve_sections: bool = True
    ) -> List[TextChunk]:
        """
        从论文结构创建文本块
        
        Args:
            paper: 论文结构
            preserve_sections: 是否按章节保留元数据
            
        Returns:
            TextChunk 列表
        """
        chunks = []
        chunk_id = 0
        
        if preserve_sections and paper.sections:
            # 按章节分块
            for section in paper.sections:
                # 清洗文本
                cleaned_text = self.clean_text(section.content)
                
                if not cleaned_text:
                    continue
                
                # 分割章节内容
                section_chunks = self.split_text_by_tokens(cleaned_text)
                
                for chunk_text in section_chunks:
                    chunk = TextChunk(
                        chunk_id=f"{paper.paper_id}_chunk_{chunk_id}",
                        paper_id=paper.paper_id,
                        text=chunk_text,
                        metadata={
                            "section_title": section.title,
                            "section_id": section.section_id,
                            "section_level": section.level,
                            "chunk_index": chunk_id
                        }
                    )
                    chunks.append(chunk)
                    chunk_id += 1
        else:
            # 全文分块
            cleaned_text = self.clean_text(paper.full_content)
            text_chunks = self.split_text_by_tokens(cleaned_text)
            
            for i, chunk_text in enumerate(text_chunks):
                chunk = TextChunk(
                    chunk_id=f"{paper.paper_id}_chunk_{i}",
                    paper_id=paper.paper_id,
                    text=chunk_text,
                    metadata={
                        "chunk_index": i
                    }
                )
                chunks.append(chunk)
        
        log.info(f"论文 {paper.paper_id} 分块完成: 共 {len(chunks)} 块")
        return chunks


# 全局处理器实例
text_processor = TextProcessor()

