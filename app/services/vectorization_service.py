"""
向量化服务
将论文文本块向量化并存储到 Milvus
"""
from typing import List, Optional

from app.models.schemas import PaperStructure, TextChunk
from app.services.text_processor import text_processor
from app.services.embedding_service import create_embedding_service
from app.services.milvus_service import milvus_service
from app.utils.logger import log
from app.utils.async_helper import TaskQueue


class VectorizationService:
    """向量化服务"""
    
    async def vectorize_and_store_paper(
        self,
        paper: PaperStructure,
        embedding_provider: Optional[str] = None,
        embedding_model: Optional[str] = None
    ) -> int:
        """
        向量化论文并存储到 Milvus
        
        Args:
            paper: 论文结构
            embedding_provider: Embedding 提供商
            embedding_model: Embedding 模型
            
        Returns:
            存储的块数量
        """
        log.info(f"开始向量化论文: {paper.paper_id}")
        
        # 1. 文本分块
        chunks = text_processor.create_chunks_from_paper(paper, preserve_sections=True)
        
        if not chunks:
            log.warning(f"论文 {paper.paper_id} 没有可分块的内容")
            return 0
        
        log.info(f"论文分块完成: {len(chunks)} 个块")
        
        # 2. 创建 Embedding 服务
        embedding_service = create_embedding_service(
            provider=embedding_provider,
            model=embedding_model
        )
        
        # 3. 获取 Embedding 维度并初始化 Milvus collection
        dimension = embedding_service.get_dimension()
        await milvus_service.create_collection(dimension=dimension)
        
        # 4. 批量生成 Embeddings
        texts = [chunk.text for chunk in chunks]
        embeddings = await embedding_service.embed_batch(texts)
        
        log.info(f"Embedding 生成完成: {len(embeddings)} 个向量")
        
        # 5. 准备数据并插入 Milvus
        chunk_ids = [chunk.chunk_id for chunk in chunks]
        paper_ids = [chunk.paper_id for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        
        await milvus_service.insert_chunks(
            chunk_ids=chunk_ids,
            paper_ids=paper_ids,
            texts=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        log.info(f"论文 {paper.paper_id} 向量化完成: 共存储 {len(chunks)} 个块")
        return len(chunks)
    
    async def delete_paper_vectors(self, paper_id: str) -> int:
        """
        删除论文的所有向量
        
        Args:
            paper_id: 论文ID
            
        Returns:
            删除的数量
        """
        count = await milvus_service.delete_by_paper_id(paper_id)
        log.info(f"删除论文 {paper_id} 的向量: {count} 个")
        return count
    
    async def search_similar_chunks(
        self,
        query_text: str,
        paper_id: Optional[str] = None,
        top_k: int = 5,
        embedding_provider: Optional[str] = None,
        embedding_model: Optional[str] = None
    ) -> List[dict]:
        """
        搜索相似的文本块
        
        Args:
            query_text: 查询文本
            paper_id: 可选的论文ID限制
            top_k: 返回结果数量
            embedding_provider: Embedding 提供商
            embedding_model: Embedding 模型
            
        Returns:
            搜索结果列表
        """
        # 生成查询向量
        embedding_service = create_embedding_service(
            provider=embedding_provider,
            model=embedding_model
        )
        
        query_embedding = await embedding_service.embed_text(query_text)
        
        # 搜索相似向量
        results = await milvus_service.search(
            query_embedding=query_embedding,
            top_k=top_k,
            paper_id=paper_id
        )
        
        log.info(f"搜索完成: 查询='{query_text[:50]}...', 结果数={len(results)}")
        return results


# 全局服务实例
vectorization_service = VectorizationService()

