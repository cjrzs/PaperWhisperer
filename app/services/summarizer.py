"""
摘要生成服务
使用 Map-Reduce 策略生成论文摘要
"""
from typing import List, Dict, Optional
import asyncio

from app.models.schemas import PaperStructure, PaperSummary, SectionSummary
from app.services.llm_factory import llm_factory
from app.utils.logger import log
from datetime import datetime


class SummarizerService:
    """摘要生成服务"""
    
    # Prompt 模板
    SECTION_SUMMARY_PROMPT = """请为以下学术论文章节生成简洁的摘要（200-300字）。

章节标题：{title}

章节内容：
{content}

请提炼该章节的核心内容、主要观点和关键发现。"""
    
    COMPREHENSIVE_SUMMARY_PROMPT = """基于以下论文的各章节摘要，生成一篇完整的综合摘要（500-800字）。

论文标题：{title}

章节摘要：
{section_summaries}

请全面概括论文的：
1. 研究背景和动机
2. 核心方法和技术
3. 主要实验和结果
4. 贡献和创新点
5. 局限性和未来工作

综合摘要："""
    
    KEY_POINTS_PROMPT = """请从以下论文摘要中提取5-8个关键要点，每个要点用一句话概括。

论文摘要：
{summary}

关键要点（使用 JSON 列表格式）："""
    
    METHODOLOGY_PROMPT = """请总结以下论文的研究方法（200-300字）。

论文内容：
{content}

方法总结："""
    
    CONTRIBUTIONS_PROMPT = """请总结以下论文的主要贡献和创新点（200-300字）。

论文内容：
{content}

贡献总结："""
    
    async def summarize_section(
        self,
        section_title: str,
        section_content: str,
        provider: Optional[str] = None
    ) -> str:
        """
        生成章节摘要
        
        Args:
            section_title: 章节标题
            section_content: 章节内容
            provider: LLM 提供商
            
        Returns:
            章节摘要
        """
        # 如果内容太长，截断
        max_length = 4000
        if len(section_content) > max_length:
            section_content = section_content[:max_length] + "...(内容已截断)"
        
        prompt = self.SECTION_SUMMARY_PROMPT.format(
            title=section_title,
            content=section_content
        )
        
        messages = [
            {"role": "system", "content": "你是专业的学术论文分析专家。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            result = await llm_factory.chat(
                messages=messages,
                provider=provider,
                temperature=0.5,
                stream=False
            )
            
            return result.strip()
            
        except Exception as e:
            log.error(f"生成章节摘要失败: {e}")
            raise
    
    async def generate_comprehensive_summary(
        self,
        title: str,
        section_summaries: List[str],
        provider: Optional[str] = None
    ) -> str:
        """
        生成综合摘要（Reduce 阶段）
        
        Args:
            title: 论文标题
            section_summaries: 章节摘要列表
            provider: LLM 提供商
            
        Returns:
            综合摘要
        """
        summaries_text = "\n\n".join([
            f"章节 {i+1}：{summary}"
            for i, summary in enumerate(section_summaries)
        ])
        
        prompt = self.COMPREHENSIVE_SUMMARY_PROMPT.format(
            title=title,
            section_summaries=summaries_text
        )
        
        messages = [
            {"role": "system", "content": "你是专业的学术论文分析专家。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            result = await llm_factory.chat(
                messages=messages,
                provider=provider,
                temperature=0.5,
                max_tokens=1500,
                stream=False
            )
            
            return result.strip()
            
        except Exception as e:
            log.error(f"生成综合摘要失败: {e}")
            raise
    
    async def extract_key_points(
        self,
        summary: str,
        provider: Optional[str] = None
    ) -> List[str]:
        """
        提取关键要点
        
        Args:
            summary: 论文摘要
            provider: LLM 提供商
            
        Returns:
            关键要点列表
        """
        prompt = self.KEY_POINTS_PROMPT.format(summary=summary)
        
        messages = [
            {"role": "system", "content": "你是专业的学术论文分析专家。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            result = await llm_factory.chat(
                messages=messages,
                provider=provider,
                temperature=0.3,
                stream=False
            )
            
            # 尝试解析 JSON 列表
            import json
            try:
                key_points = json.loads(result.strip())
                if isinstance(key_points, list):
                    return key_points
            except:
                pass
            
            # 如果不是 JSON，按行分割
            lines = [line.strip() for line in result.strip().split('\n') if line.strip()]
            # 移除列表标记（如 "1. ", "- " 等）
            import re
            key_points = [re.sub(r'^[\d\-\*\+\.]+\s*', '', line) for line in lines]
            return [kp for kp in key_points if kp]
            
        except Exception as e:
            log.error(f"提取关键要点失败: {e}")
            return []
    
    async def summarize_methodology(
        self,
        content: str,
        provider: Optional[str] = None
    ) -> str:
        """
        总结研究方法
        
        Args:
            content: 论文内容（通常是方法章节）
            provider: LLM 提供商
            
        Returns:
            方法总结
        """
        # 截断内容
        max_length = 4000
        if len(content) > max_length:
            content = content[:max_length] + "...(内容已截断)"
        
        prompt = self.METHODOLOGY_PROMPT.format(content=content)
        
        messages = [
            {"role": "system", "content": "你是专业的学术论文分析专家。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            result = await llm_factory.chat(
                messages=messages,
                provider=provider,
                temperature=0.5,
                stream=False
            )
            
            return result.strip()
            
        except Exception as e:
            log.error(f"总结方法失败: {e}")
            return ""
    
    async def summarize_contributions(
        self,
        content: str,
        provider: Optional[str] = None
    ) -> str:
        """
        总结主要贡献
        
        Args:
            content: 论文内容（通常是结论或摘要）
            provider: LLM 提供商
            
        Returns:
            贡献总结
        """
        # 截断内容
        max_length = 4000
        if len(content) > max_length:
            content = content[:max_length] + "...(内容已截断)"
        
        prompt = self.CONTRIBUTIONS_PROMPT.format(content=content)
        
        messages = [
            {"role": "system", "content": "你是专业的学术论文分析专家。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            result = await llm_factory.chat(
                messages=messages,
                provider=provider,
                temperature=0.5,
                stream=False
            )
            
            return result.strip()
            
        except Exception as e:
            log.error(f"总结贡献失败: {e}")
            return ""
    
    async def summarize_paper(
        self,
        paper: PaperStructure,
        provider: Optional[str] = None,
        summary_type: str = "comprehensive"
    ) -> PaperSummary:
        """
        生成论文摘要（完整流程）
        
        Args:
            paper: 论文结构
            provider: LLM 提供商
            summary_type: 摘要类型（comprehensive/brief/technical）
            
        Returns:
            论文摘要对象
        """
        log.info(f"开始生成论文摘要: {paper.paper_id}, 类型: {summary_type}")
        
        try:
            # Map 阶段：生成各章节摘要
            section_summaries = []
            
            if paper.sections:
                tasks = []
                for section in paper.sections:
                    # 跳过太短的章节
                    if len(section.content) < 100:
                        continue
                    
                    task = self.summarize_section(
                        section_title=section.title,
                        section_content=section.content,
                        provider=provider
                    )
                    tasks.append((section.title, task))
                
                # 并发执行（但限制并发数避免限流）
                for i in range(0, len(tasks), 3):  # 每次3个
                    batch = tasks[i:i+3]
                    results = await asyncio.gather(*[t[1] for t in batch])
                    
                    for (title, _), summary in zip(batch, results):
                        section_summaries.append(
                            SectionSummary(section_title=title, summary=summary)
                        )
                    
                    # 避免限流
                    if i + 3 < len(tasks):
                        await asyncio.sleep(1)
            
            # Reduce 阶段：生成综合摘要
            summary_texts = [s.summary for s in section_summaries]
            overall_summary = await self.generate_comprehensive_summary(
                title=paper.metadata.title or "未知标题",
                section_summaries=summary_texts,
                provider=provider
            )
            
            # 提取关键要点
            key_points = await self.extract_key_points(overall_summary, provider=provider)
            
            # 总结方法（从相关章节提取）
            methodology_content = ""
            for section in paper.sections:
                if any(keyword in section.title.lower() for keyword in ['method', 'approach', '方法', 'algorithm']):
                    methodology_content += section.content + "\n\n"
            
            methodology = ""
            if methodology_content:
                methodology = await self.summarize_methodology(methodology_content, provider=provider)
            
            # 总结贡献（从摘要或结论提取）
            contributions_content = paper.metadata.abstract or ""
            for section in paper.sections:
                if any(keyword in section.title.lower() for keyword in ['conclusion', 'contribution', '结论', '贡献']):
                    contributions_content += section.content + "\n\n"
            
            contributions = ""
            if contributions_content:
                contributions = await self.summarize_contributions(contributions_content, provider=provider)
            
            # 构建最终摘要对象
            paper_summary = PaperSummary(
                paper_id=paper.paper_id,
                overall_summary=overall_summary,
                key_points=key_points,
                methodology=methodology if methodology else None,
                contributions=contributions if contributions else None,
                section_summaries=section_summaries,
                created_at=datetime.now()
            )
            
            log.info(f"论文摘要生成完成: {paper.paper_id}")
            return paper_summary
            
        except Exception as e:
            log.error(f"生成论文摘要失败: {e}")
            raise


# 全局服务实例
summarizer_service = SummarizerService()

