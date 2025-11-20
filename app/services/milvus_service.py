"""
Milvus 向量数据库服务
用于存储和检索论文向量
"""
from typing import List, Dict, Any, Optional
from pymilvus import (
    connections,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility
)
import json

from app.config import settings
from app.utils.logger import log


class MilvusService:
    """Milvus 向量数据库服务"""
    
    def __init__(self):
        self.host = settings.milvus_host
        self.port = settings.milvus_port
        self.collection_name = settings.milvus_collection_name
        self.collection: Optional[Collection] = None
        self._connected = False
    
    async def connect(self):
        """连接到 Milvus"""
        if self._connected:
            return
        
        try:
            connections.connect(
                alias="default",
                host=self.host,
                port=self.port
            )
            self._connected = True
            log.info(f"成功连接到 Milvus: {self.host}:{self.port}")
            
        except Exception as e:
            log.error(f"连接 Milvus 失败: {e}")
            raise
    
    async def disconnect(self):
        """断开连接"""
        if self._connected:
            connections.disconnect("default")
            self._connected = False
            log.info("已断开 Milvus 连接")
    
    async def create_collection(self, dimension: int = 1536):
        """
        创建 collection
        
        Args:
            dimension: Embedding 向量维度
        """
        await self.connect()
        
        # 检查 collection 是否已存在
        if utility.has_collection(self.collection_name):
            log.info(f"Collection {self.collection_name} 已存在")
            self.collection = Collection(self.collection_name)
            return
        
        # 定义 schema
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="chunk_id", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="paper_id", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="chunk_text", dtype=DataType.VARCHAR, max_length=10000),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dimension),
            FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=5000)  # JSON string
        ]
        
        schema = CollectionSchema(
            fields=fields,
            description="论文文本块向量存储"
        )
        
        # 创建 collection
        self.collection = Collection(
            name=self.collection_name,
            schema=schema
        )
        
        # 创建索引（HNSW 索引适合高维向量）
        index_params = {
            "metric_type": "IP",  # Inner Product (适合归一化向量)
            "index_type": "HNSW",
            "params": {"M": 8, "efConstruction": 200}
        }
        
        self.collection.create_index(
            field_name="embedding",
            index_params=index_params
        )
        
        log.info(f"成功创建 collection: {self.collection_name}, 维度: {dimension}")
    
    async def insert_chunks(
        self,
        chunk_ids: List[str],
        paper_ids: List[str],
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]]
    ) -> List[int]:
        """
        插入文本块
        
        Args:
            chunk_ids: 块ID列表
            paper_ids: 论文ID列表
            texts: 文本列表
            embeddings: Embedding 列表
            metadatas: 元数据列表
            
        Returns:
            插入的ID列表
        """
        await self.connect()
        
        if not self.collection:
            raise RuntimeError("Collection 未初始化")
        
        # 将元数据转为 JSON 字符串
        metadata_strs = [json.dumps(m, ensure_ascii=False) for m in metadatas]
        
        # 准备数据
        data = [
            chunk_ids,
            paper_ids,
            texts,
            embeddings,
            metadata_strs
        ]
        
        try:
            # 插入数据
            insert_result = self.collection.insert(data)
            
            # 刷新确保数据持久化
            self.collection.flush()
            
            log.info(f"成功插入 {len(chunk_ids)} 个文本块")
            return insert_result.primary_keys
            
        except Exception as e:
            log.error(f"插入数据失败: {e}")
            raise
    
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        paper_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        向量检索
        
        Args:
            query_embedding: 查询向量
            top_k: 返回结果数量
            paper_id: 可选的论文ID过滤
            
        Returns:
            检索结果列表
        """
        await self.connect()
        
        if not self.collection:
            raise RuntimeError("Collection 未初始化")
        
        # 加载 collection 到内存
        self.collection.load()
        
        # 搜索参数
        search_params = {
            "metric_type": "IP",
            "params": {"ef": 100}
        }
        
        # 表达式过滤（如果指定了 paper_id）
        expr = f'paper_id == "{paper_id}"' if paper_id else None
        
        try:
            # 执行搜索
            results = self.collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                expr=expr,
                output_fields=["chunk_id", "paper_id", "chunk_text", "metadata"]
            )
            
            # 格式化结果
            formatted_results = []
            for hit in results[0]:
                metadata = json.loads(hit.entity.get("metadata", "{}"))
                formatted_results.append({
                    "chunk_id": hit.entity.get("chunk_id"),
                    "paper_id": hit.entity.get("paper_id"),
                    "text": hit.entity.get("chunk_text"),
                    "score": hit.score,
                    "metadata": metadata
                })
            
            log.info(f"检索到 {len(formatted_results)} 个相关结果")
            return formatted_results
            
        except Exception as e:
            log.error(f"向量检索失败: {e}")
            raise
    
    async def delete_by_paper_id(self, paper_id: str) -> int:
        """
        删除指定论文的所有数据
        
        Args:
            paper_id: 论文ID
            
        Returns:
            删除的数量
        """
        await self.connect()
        
        if not self.collection:
            raise RuntimeError("Collection 未初始化")
        
        try:
            expr = f'paper_id == "{paper_id}"'
            delete_result = self.collection.delete(expr)
            
            self.collection.flush()
            
            log.info(f"删除论文 {paper_id} 的数据")
            return delete_result.delete_count
            
        except Exception as e:
            log.error(f"删除数据失败: {e}")
            raise
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        获取 collection 统计信息
        
        Returns:
            统计信息
        """
        await self.connect()
        
        if not self.collection:
            return {"error": "Collection 未初始化"}
        
        try:
            self.collection.load()
            num_entities = self.collection.num_entities
            
            return {
                "collection_name": self.collection_name,
                "num_entities": num_entities,
                "schema": str(self.collection.schema)
            }
            
        except Exception as e:
            log.error(f"获取统计信息失败: {e}")
            return {"error": str(e)}


# 全局服务实例
milvus_service = MilvusService()

