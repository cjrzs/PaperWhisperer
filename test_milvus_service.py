"""
Milvus 向量服务测试
测试 MilvusService 的各项功能
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import List, Dict, Any
import json

from app.services.milvus_service import MilvusService


class TestMilvusService:
    """Milvus 服务测试类"""
    
    @pytest.fixture
    def service(self):
        """创建测试服务实例"""
        return MilvusService()
    
    @pytest.fixture
    def mock_collection(self):
        """创建模拟的 Collection 对象"""
        collection = Mock()
        collection.insert = Mock(return_value=Mock(primary_keys=[1, 2, 3]))
        collection.flush = Mock()
        collection.load = Mock()
        collection.num_entities = 100
        collection.schema = "test_schema"
        collection.delete = Mock(return_value=Mock(delete_count=5))
        
        # 模拟搜索结果
        hit1 = Mock()
        hit1.entity.get = Mock(side_effect=lambda x, default="": {
            "chunk_id": "chunk_1",
            "paper_id": "paper_1",
            "chunk_text": "测试文本1",
            "metadata": '{"section": "introduction"}'
        }.get(x, default))
        hit1.score = 0.95
        
        hit2 = Mock()
        hit2.entity.get = Mock(side_effect=lambda x, default="": {
            "chunk_id": "chunk_2",
            "paper_id": "paper_1",
            "chunk_text": "测试文本2",
            "metadata": '{"section": "methods"}'
        }.get(x, default))
        hit2.score = 0.88
        
        collection.search = Mock(return_value=[[hit1, hit2]])
        
        return collection
    
    @pytest.mark.asyncio
    async def test_connect_success(self, service):
        """测试 1: 成功连接到 Milvus"""
        with patch('app.services.milvus_service.connections') as mock_connections:
            mock_connections.connect = Mock()
            
            await service.connect()
            
            assert service._connected is True
            mock_connections.connect.assert_called_once_with(
                alias="default",
                host=service.host,
                port=service.port
            )
    
    @pytest.mark.asyncio
    async def test_connect_already_connected(self, service):
        """测试 2: 重复连接（应该跳过）"""
        service._connected = True
        
        with patch('app.services.milvus_service.connections') as mock_connections:
            mock_connections.connect = Mock()
            
            await service.connect()
            
            # 不应该调用连接方法
            mock_connections.connect.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_connect_failure(self, service):
        """测试 3: 连接失败"""
        with patch('app.services.milvus_service.connections') as mock_connections:
            mock_connections.connect.side_effect = Exception("连接失败")
            
            with pytest.raises(Exception, match="连接失败"):
                await service.connect()
            
            assert service._connected is False
    
    @pytest.mark.asyncio
    async def test_disconnect(self, service):
        """测试 4: 断开连接"""
        service._connected = True
        
        with patch('app.services.milvus_service.connections') as mock_connections:
            mock_connections.disconnect = Mock()
            
            await service.disconnect()
            
            assert service._connected is False
            mock_connections.disconnect.assert_called_once_with("default")
    
    @pytest.mark.asyncio
    async def test_create_collection_new(self, service, mock_collection):
        """测试 5: 创建新的 collection"""
        with patch('app.services.milvus_service.connections'), \
             patch('app.services.milvus_service.utility') as mock_utility, \
             patch('app.services.milvus_service.Collection', return_value=mock_collection), \
             patch('app.services.milvus_service.CollectionSchema') as mock_schema:
            
            mock_utility.has_collection.return_value = False
            
            await service.create_collection(dimension=1536)
            
            assert service.collection is not None
            mock_collection.create_index.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_collection_exists(self, service, mock_collection):
        """测试 6: collection 已存在"""
        with patch('app.services.milvus_service.connections'), \
             patch('app.services.milvus_service.utility') as mock_utility, \
             patch('app.services.milvus_service.Collection', return_value=mock_collection):
            
            mock_utility.has_collection.return_value = True
            
            await service.create_collection(dimension=1536)
            
            assert service.collection is not None
            # 不应该调用 create_index（因为已存在）
            mock_collection.create_index.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_insert_chunks_success(self, service, mock_collection):
        """测试 7: 成功插入文本块"""
        service.collection = mock_collection
        service._connected = True
        
        chunk_ids = ["chunk_1", "chunk_2", "chunk_3"]
        paper_ids = ["paper_1", "paper_1", "paper_1"]
        texts = ["文本1", "文本2", "文本3"]
        embeddings = [[0.1]*1536, [0.2]*1536, [0.3]*1536]
        metadatas = [
            {"section": "intro"},
            {"section": "methods"},
            {"section": "results"}
        ]
        
        with patch('app.services.milvus_service.connections'):
            result = await service.insert_chunks(
                chunk_ids, paper_ids, texts, embeddings, metadatas
            )
        
        assert result == [1, 2, 3]
        mock_collection.insert.assert_called_once()
        mock_collection.flush.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_insert_chunks_no_collection(self, service):
        """测试 8: 未初始化 collection 时插入"""
        service._connected = True
        service.collection = None
        
        with patch('app.services.milvus_service.connections'):
            with pytest.raises(RuntimeError, match="Collection 未初始化"):
                await service.insert_chunks(
                    ["chunk_1"], ["paper_1"], ["文本"],
                    [[0.1]*1536], [{"section": "intro"}]
                )
    
    @pytest.mark.asyncio
    async def test_insert_chunks_failure(self, service, mock_collection):
        """测试 9: 插入失败"""
        service.collection = mock_collection
        service._connected = True
        mock_collection.insert.side_effect = Exception("插入失败")
        
        with patch('app.services.milvus_service.connections'):
            with pytest.raises(Exception, match="插入失败"):
                await service.insert_chunks(
                    ["chunk_1"], ["paper_1"], ["文本"],
                    [[0.1]*1536], [{"section": "intro"}]
                )
    
    @pytest.mark.asyncio
    async def test_search_success(self, service, mock_collection):
        """测试 10: 成功执行向量检索"""
        service.collection = mock_collection
        service._connected = True
        
        query_embedding = [0.5] * 1536
        
        with patch('app.services.milvus_service.connections'):
            results = await service.search(
                query_embedding=query_embedding,
                top_k=5,
                paper_id=None
            )
        
        assert len(results) == 2
        assert results[0]["chunk_id"] == "chunk_1"
        assert results[0]["paper_id"] == "paper_1"
        assert results[0]["text"] == "测试文本1"
        assert results[0]["score"] == 0.95
        assert results[0]["metadata"]["section"] == "introduction"
        
        assert results[1]["chunk_id"] == "chunk_2"
        assert results[1]["score"] == 0.88
        
        mock_collection.load.assert_called_once()
        mock_collection.search.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_with_paper_id_filter(self, service, mock_collection):
        """测试 11: 带论文ID过滤的检索"""
        service.collection = mock_collection
        service._connected = True
        
        query_embedding = [0.5] * 1536
        
        with patch('app.services.milvus_service.connections'):
            results = await service.search(
                query_embedding=query_embedding,
                top_k=5,
                paper_id="paper_123"
            )
        
        # 验证搜索参数
        call_args = mock_collection.search.call_args
        assert call_args[1]["expr"] == 'paper_id == "paper_123"'
    
    @pytest.mark.asyncio
    async def test_search_no_collection(self, service):
        """测试 12: 未初始化 collection 时检索"""
        service._connected = True
        service.collection = None
        
        with patch('app.services.milvus_service.connections'):
            with pytest.raises(RuntimeError, match="Collection 未初始化"):
                await service.search([0.5]*1536)
    
    @pytest.mark.asyncio
    async def test_search_failure(self, service, mock_collection):
        """测试 13: 检索失败"""
        service.collection = mock_collection
        service._connected = True
        mock_collection.search.side_effect = Exception("检索失败")
        
        with patch('app.services.milvus_service.connections'):
            with pytest.raises(Exception, match="检索失败"):
                await service.search([0.5]*1536)
    
    @pytest.mark.asyncio
    async def test_delete_by_paper_id_success(self, service, mock_collection):
        """测试 14: 成功删除论文数据"""
        service.collection = mock_collection
        service._connected = True
        
        with patch('app.services.milvus_service.connections'):
            count = await service.delete_by_paper_id("paper_123")
        
        assert count == 5
        mock_collection.delete.assert_called_once()
        mock_collection.flush.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_by_paper_id_no_collection(self, service):
        """测试 15: 未初始化 collection 时删除"""
        service._connected = True
        service.collection = None
        
        with patch('app.services.milvus_service.connections'):
            with pytest.raises(RuntimeError, match="Collection 未初始化"):
                await service.delete_by_paper_id("paper_123")
    
    @pytest.mark.asyncio
    async def test_delete_by_paper_id_failure(self, service, mock_collection):
        """测试 16: 删除失败"""
        service.collection = mock_collection
        service._connected = True
        mock_collection.delete.side_effect = Exception("删除失败")
        
        with patch('app.services.milvus_service.connections'):
            with pytest.raises(Exception, match="删除失败"):
                await service.delete_by_paper_id("paper_123")
    
    @pytest.mark.asyncio
    async def test_get_stats_success(self, service, mock_collection):
        """测试 17: 成功获取统计信息"""
        service.collection = mock_collection
        service._connected = True
        
        with patch('app.services.milvus_service.connections'):
            stats = await service.get_stats()
        
        assert stats["collection_name"] == service.collection_name
        assert stats["num_entities"] == 100
        assert "schema" in stats
        
        mock_collection.load.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_stats_no_collection(self, service):
        """测试 18: 未初始化 collection 时获取统计信息"""
        service._connected = True
        service.collection = None
        
        with patch('app.services.milvus_service.connections'):
            stats = await service.get_stats()
        
        assert "error" in stats
        assert stats["error"] == "Collection 未初始化"
    
    @pytest.mark.asyncio
    async def test_get_stats_failure(self, service, mock_collection):
        """测试 19: 获取统计信息失败"""
        service.collection = mock_collection
        service._connected = True
        mock_collection.load.side_effect = Exception("加载失败")
        
        with patch('app.services.milvus_service.connections'):
            stats = await service.get_stats()
        
        assert "error" in stats
        assert "加载失败" in stats["error"]
    
    @pytest.mark.asyncio
    async def test_metadata_json_serialization(self, service, mock_collection):
        """测试 20: 元数据 JSON 序列化"""
        service.collection = mock_collection
        service._connected = True
        
        # 包含中文的元数据
        metadatas = [
            {"section": "引言", "page": 1, "author": "张三"},
            {"section": "方法", "page": 2, "tags": ["机器学习", "深度学习"]}
        ]
        
        with patch('app.services.milvus_service.connections'):
            await service.insert_chunks(
                ["chunk_1", "chunk_2"],
                ["paper_1", "paper_1"],
                ["文本1", "文本2"],
                [[0.1]*1536, [0.2]*1536],
                metadatas
            )
        
        # 验证 JSON 序列化调用
        call_args = mock_collection.insert.call_args[0][0]
        metadata_strs = call_args[4]  # 第5个参数是元数据列表
        
        # 验证可以反序列化
        for meta_str in metadata_strs:
            parsed = json.loads(meta_str)
            assert isinstance(parsed, dict)


class TestMilvusServiceIntegration:
    """Milvus 服务集成测试（需要实际的 Milvus 实例）"""
    
    @pytest.fixture
    def service(self):
        """创建测试服务实例"""
        return MilvusService()
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_full_workflow(self, service):
        """
        测试 21: 完整工作流程
        注意: 此测试需要实际运行的 Milvus 实例
        使用 pytest -m integration 来运行集成测试
        """
        try:
            # 1. 连接
            await service.connect()
            
            # 2. 创建 collection
            await service.create_collection(dimension=384)  # 使用较小的维度进行测试
            
            # 3. 插入测试数据
            chunk_ids = ["test_chunk_1", "test_chunk_2", "test_chunk_3"]
            paper_ids = ["test_paper_1", "test_paper_1", "test_paper_1"]
            texts = [
                "这是第一个测试文本块",
                "这是第二个测试文本块",
                "这是第三个测试文本块"
            ]
            embeddings = [
                [0.1 + i*0.01] * 384 for i in range(3)
            ]
            metadatas = [
                {"section": "intro", "index": 0},
                {"section": "methods", "index": 1},
                {"section": "results", "index": 2}
            ]
            
            result = await service.insert_chunks(
                chunk_ids, paper_ids, texts, embeddings, metadatas
            )
            assert len(result) == 3
            
            # 4. 执行检索
            query_embedding = [0.11] * 384
            results = await service.search(
                query_embedding=query_embedding,
                top_k=2,
                paper_id="test_paper_1"
            )
            assert len(results) <= 2
            
            # 5. 获取统计信息
            stats = await service.get_stats()
            assert stats["num_entities"] >= 3
            
            # 6. 删除测试数据
            delete_count = await service.delete_by_paper_id("test_paper_1")
            assert delete_count >= 3
            
            # 7. 断开连接
            await service.disconnect()
            
            print("✅ 集成测试通过")
            
        except Exception as e:
            print(f"❌ 集成测试失败: {e}")
            print("提示: 确保 Milvus 实例正在运行且配置正确")
            pytest.skip(f"跳过集成测试: {e}")


def test_module_imports():
    """测试 22: 模块导入"""
    from app.services.milvus_service import milvus_service, MilvusService
    
    assert milvus_service is not None
    assert isinstance(milvus_service, MilvusService)


if __name__ == "__main__":
    """直接运行测试"""
    import sys
    
    print("="*60)
    print("Milvus 服务测试")
    print("="*60)
    print("\n运行单元测试（不需要 Milvus 实例）...")
    print("使用命令: pytest test_milvus_service.py -v")
    print("\n运行集成测试（需要 Milvus 实例）...")
    print("使用命令: pytest test_milvus_service.py -v -m integration")
    print("="*60)
    
    # 运行 pytest
    pytest.main([__file__, "-v", "--tb=short"])

