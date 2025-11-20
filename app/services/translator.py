"""
论文翻译服务
提供高质量的学术论文翻译
"""
from typing import List, Dict, Optional
import asyncio

from app.models.schemas import PaperStructure, TranslationSegment, TranslationResult, TaskStatus
from app.services.llm_factory import llm_factory
from app.utils.logger import log
from datetime import datetime


class TranslationService:
    """翻译服务"""
    
    # 翻译 Prompt 模板
    TRANSLATION_PROMPT = """你是一位专业的学术论文翻译专家。请将以下{source_lang}学术论文文本翻译成{target_lang}。

翻译要求：
1. 保持学术专业性和严谨性
2. 专业术语翻译准确，保持一致性
3. 语句流畅自然，符合目标语言的学术表达习惯
4. 保留原文的公式、引用格式和特殊标记
5. 不要添加任何解释或额外内容，只返回翻译结果

原文：
{text}

翻译："""
    
    CONTEXT_PROMPT = """请注意，这是论文的一部分，以下是上下文信息：

前文片段：
{prev_context}

当前需要翻译的文本：
{text}

后文片段：
{next_context}

请根据上下文翻译当前文本，确保术语和表达的连贯性。只返回当前文本的翻译，不要翻译上下文部分。"""
    
    async def translate_text(
        self,
        text: str,
        source_lang: str = "英文",
        target_lang: str = "中文",
        provider: Optional[str] = None,
        prev_context: Optional[str] = None,
        next_context: Optional[str] = None
    ) -> str:
        """
        翻译单段文本
        
        Args:
            text: 要翻译的文本
            source_lang: 源语言
            target_lang: 目标语言
            provider: LLM 提供商
            prev_context: 前文上下文
            next_context: 后文上下文
            
        Returns:
            翻译结果
        """
        # 构建 prompt
        if prev_context or next_context:
            prompt = self.CONTEXT_PROMPT.format(
                prev_context=prev_context or "(无)",
                text=text,
                next_context=next_context or "(无)"
            )
        else:
            prompt = self.TRANSLATION_PROMPT.format(
                source_lang=source_lang,
                target_lang=target_lang,
                text=text
            )
        
        messages = [
            {"role": "system", "content": "你是专业的学术论文翻译专家。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            result = await llm_factory.chat(
                messages=messages,
                provider=provider,
                temperature=0.3,  # 较低温度以提高一致性
                stream=False
            )
            
            return result.strip()
            
        except Exception as e:
            log.error(f"翻译失败: {e}")
            raise
    
    async def translate_paper(
        self,
        paper: PaperStructure,
        source_lang: str = "英文",
        target_lang: str = "中文",
        provider: Optional[str] = None,
        translate_by_section: bool = True
    ) -> TranslationResult:
        """
        翻译整篇论文
        
        Args:
            paper: 论文结构
            source_lang: 源语言
            target_lang: 目标语言
            provider: LLM 提供商
            translate_by_section: 是否按章节翻译
            
        Returns:
            翻译结果
        """
        log.info(f"开始翻译论文: {paper.paper_id}, 章节数: {len(paper.sections)}")
        
        segments: List[TranslationSegment] = []
        
        try:
            if translate_by_section and paper.sections:
                # 按章节翻译
                for i, section in enumerate(paper.sections):
                    log.info(f"翻译章节 {i+1}/{len(paper.sections)}: {section.title}")
                    
                    # 如果章节内容太长，需要分段
                    if len(section.content) > 3000:  # 字符数限制
                        subsegments = await self._translate_long_section(
                            section.content,
                            section.title,
                            source_lang,
                            target_lang,
                            provider
                        )
                        segments.extend(subsegments)
                    else:
                        # 翻译整个章节
                        translated = await self.translate_text(
                            text=section.content,
                            source_lang=source_lang,
                            target_lang=target_lang,
                            provider=provider
                        )
                        
                        segment = TranslationSegment(
                            original=section.content,
                            translated=translated,
                            section_title=section.title
                        )
                        segments.append(segment)
                    
                    # 避免 API 限流
                    await asyncio.sleep(0.5)
            else:
                # 全文翻译（分段处理）
                full_text = paper.full_content
                subsegments = await self._translate_long_section(
                    full_text,
                    None,
                    source_lang,
                    target_lang,
                    provider
                )
                segments.extend(subsegments)
            
            result = TranslationResult(
                paper_id=paper.paper_id,
                segments=segments,
                status=TaskStatus.COMPLETED,
                created_at=datetime.now()
            )
            
            log.info(f"论文翻译完成: {paper.paper_id}, 段落数: {len(segments)}")
            return result
            
        except Exception as e:
            log.error(f"论文翻译失败: {e}")
            result = TranslationResult(
                paper_id=paper.paper_id,
                segments=segments,  # 保存已翻译的部分
                status=TaskStatus.FAILED,
                created_at=datetime.now()
            )
            return result
    
    async def _translate_long_section(
        self,
        text: str,
        section_title: Optional[str],
        source_lang: str,
        target_lang: str,
        provider: Optional[str]
    ) -> List[TranslationSegment]:
        """
        翻译长文本（分段处理，保留上下文）
        
        Args:
            text: 文本内容
            section_title: 章节标题
            source_lang: 源语言
            target_lang: 目标语言
            provider: LLM 提供商
            
        Returns:
            翻译片段列表
        """
        # 按段落分割
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        segments = []
        context_size = 200  # 上下文字符数
        
        for i, para in enumerate(paragraphs):
            # 获取上下文
            prev_context = paragraphs[i-1][-context_size:] if i > 0 else None
            next_context = paragraphs[i+1][:context_size] if i < len(paragraphs) - 1 else None
            
            # 翻译段落
            translated = await self.translate_text(
                text=para,
                source_lang=source_lang,
                target_lang=target_lang,
                provider=provider,
                prev_context=prev_context,
                next_context=next_context
            )
            
            segment = TranslationSegment(
                original=para,
                translated=translated,
                section_title=section_title
            )
            segments.append(segment)
            
            # 避免限流
            await asyncio.sleep(0.3)
        
        return segments
    
    async def translate_abstract(
        self,
        abstract: str,
        source_lang: str = "英文",
        target_lang: str = "中文",
        provider: Optional[str] = None
    ) -> str:
        """
        翻译摘要（快速翻译）
        
        Args:
            abstract: 摘要文本
            source_lang: 源语言
            target_lang: 目标语言
            provider: LLM 提供商
            
        Returns:
            翻译后的摘要
        """
        return await self.translate_text(
            text=abstract,
            source_lang=source_lang,
            target_lang=target_lang,
            provider=provider
        )


# 全局服务实例
translation_service = TranslationService()

