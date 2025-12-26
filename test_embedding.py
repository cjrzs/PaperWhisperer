"""
Embedding 服务测试脚本
测试 embedding 接口的各项功能
"""
import asyncio
import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from app.services.embedding_service import EmbeddingService, create_embedding_service
from app.config import settings
from app.utils.logger import log


class EmbeddingTester:
    """Embedding 测试类"""
    
    def __init__(self, provider: str = None):
        """初始化测试器"""
        self.provider = provider or settings.default_embedding_provider
        self.service = None
        self.test_results = []
    
    async def test_initialization(self):
        """测试 1: 初始化服务"""
        print("\n" + "="*60)
        print("测试 1: 初始化 Embedding 服务")
        print("="*60)
        
        try:
            self.service = create_embedding_service(provider=self.provider)
            print(f"✅ 服务初始化成功")
            print(f"   提供商: {self.service.provider}")
            print(f"   模型: {self.service.model}")
            print(f"   Base URL: {self.service.config['base_url']}")
            self.test_results.append(("初始化服务", True, None))
            return True
        except Exception as e:
            print(f"❌ 服务初始化失败: {e}")
            self.test_results.append(("初始化服务", False, str(e)))
            return False
    
    async def test_single_embedding(self):
        """测试 2: 单个文本的 embedding"""
        print("\n" + "="*60)
        print("测试 2: 生成单个文本的 Embedding")
        print("="*60)
        
        test_text = "This is a test sentence for embedding generation."
        print(f"测试文本: {test_text}")
        
        try:
            embedding = await self.service.embed_text(test_text)
            print(f"✅ Embedding 生成成功")
            print(f"   向量维度: {len(embedding)}")
            print(f"   向量类型: {type(embedding)}")
            print(f"   前5个值: {embedding[:5]}")
            
            # 验证维度
            expected_dim = self.service.get_dimension()
            if len(embedding) == expected_dim:
                print(f"   ✅ 维度验证通过 (期望: {expected_dim})")
            else:
                print(f"   ⚠️  维度不匹配 (期望: {expected_dim}, 实际: {len(embedding)})")
            
            self.test_results.append(("单个文本embedding", True, None))
            return True
        except Exception as e:
            print(f"❌ Embedding 生成失败: {e}")
            self.test_results.append(("单个文本embedding", False, str(e)))
            return False
    
    async def test_batch_embedding(self):
        """测试 3: 批量文本的 embedding"""
        print("\n" + "="*60)
        print("测试 3: 批量生成 Embedding")
        print("="*60)
        
        test_texts = [
            "The quick brown fox jumps over the lazy dog.",
            "Machine learning is a subset of artificial intelligence.",
            "Python is a popular programming language for data science.",
            "Natural language processing enables computers to understand human language.",
            "Deep learning models require large amounts of training data."
        ]
        
        print(f"测试文本数量: {len(test_texts)}")
        for i, text in enumerate(test_texts, 1):
            print(f"  {i}. {text[:50]}...")
        
        try:
            embeddings = await self.service.embed_batch(test_texts)
            print(f"✅ 批量 Embedding 生成成功")
            print(f"   生成数量: {len(embeddings)}")
            print(f"   向量维度: {len(embeddings[0])}")
            
            # 验证数量
            if len(embeddings) == len(test_texts):
                print(f"   ✅ 数量验证通过")
            else:
                print(f"   ⚠️  数量不匹配 (期望: {len(test_texts)}, 实际: {len(embeddings)})")
            
            # 验证所有向量维度一致
            dims = [len(emb) for emb in embeddings]
            if len(set(dims)) == 1:
                print(f"   ✅ 所有向量维度一致")
            else:
                print(f"   ⚠️  向量维度不一致: {dims}")
            
            self.test_results.append(("批量embedding", True, None))
            return True
        except Exception as e:
            print(f"❌ 批量 Embedding 生成失败: {e}")
            self.test_results.append(("批量embedding", False, str(e)))
            return False
    
    async def test_empty_input(self):
        """测试 4: 空输入处理"""
        print("\n" + "="*60)
        print("测试 4: 空输入处理")
        print("="*60)
        
        try:
            # 测试空列表
            embeddings = await self.service.embed_batch([])
            if embeddings == []:
                print(f"✅ 空列表处理正确")
                self.test_results.append(("空输入处理", True, None))
                return True
            else:
                print(f"⚠️  空列表返回了非空结果: {embeddings}")
                self.test_results.append(("空输入处理", False, "空列表返回非空结果"))
                return False
        except Exception as e:
            print(f"❌ 空输入处理失败: {e}")
            self.test_results.append(("空输入处理", False, str(e)))
            return False
    
    async def test_chinese_text(self):
        """测试 5: 中文文本 embedding"""
        print("\n" + "="*60)
        print("测试 5: 中文文本 Embedding")
        print("="*60)
        
        test_texts = [
            "人工智能是计算机科学的一个分支。",
            "自然语言处理技术可以帮助计算机理解人类语言。",
            "深度学习模型需要大量的训练数据。"
        ]
        
        print(f"测试中文文本数量: {len(test_texts)}")
        for i, text in enumerate(test_texts, 1):
            print(f"  {i}. {text}")
        
        try:
            embeddings = await self.service.embed_batch(test_texts)
            print(f"✅ 中文文本 Embedding 生成成功")
            print(f"   生成数量: {len(embeddings)}")
            print(f"   向量维度: {len(embeddings[0])}")
            
            self.test_results.append(("中文文本embedding", True, None))
            return True
        except Exception as e:
            print(f"❌ 中文文本 Embedding 生成失败: {e}")
            self.test_results.append(("中文文本embedding", False, str(e)))
            return False
    
    async def test_long_text(self):
        """测试 6: 长文本 embedding"""
        print("\n" + "="*60)
        print("测试 6: 长文本 Embedding")
        print("="*60)
        
        # 生成一个较长的文本（约500个单词）
        long_text = " ".join([
            "Artificial intelligence and machine learning have revolutionized the way we approach complex problems in various domains."
        ] * 50)
        
        print(f"测试文本长度: {len(long_text)} 字符")
        print(f"文本预览: {long_text[:100]}...")
        
        try:
            embedding = await self.service.embed_text(long_text)
            print(f"✅ 长文本 Embedding 生成成功")
            print(f"   向量维度: {len(embedding)}")
            
            self.test_results.append(("长文本embedding", True, None))
            return True
        except Exception as e:
            print(f"❌ 长文本 Embedding 生成失败: {e}")
            self.test_results.append(("长文本embedding", False, str(e)))
            return False
    
    async def test_dimension_consistency(self):
        """测试 7: 维度一致性"""
        print("\n" + "="*60)
        print("测试 7: 不同文本长度的维度一致性")
        print("="*60)
        
        test_texts = [
            "Short.",
            "This is a medium length sentence.",
            "This is a much longer sentence that contains significantly more words and information than the previous ones.",
        ]
        
        try:
            embeddings = []
            for text in test_texts:
                emb = await self.service.embed_text(text)
                embeddings.append(emb)
                print(f"   文本长度: {len(text):3d} 字符 -> 向量维度: {len(emb)}")
            
            # 检查维度是否一致
            dims = [len(emb) for emb in embeddings]
            if len(set(dims)) == 1:
                print(f"✅ 所有文本的 embedding 维度一致: {dims[0]}")
                self.test_results.append(("维度一致性", True, None))
                return True
            else:
                print(f"⚠️  维度不一致: {dims}")
                self.test_results.append(("维度一致性", False, f"维度不一致: {dims}"))
                return False
        except Exception as e:
            print(f"❌ 维度一致性测试失败: {e}")
            self.test_results.append(("维度一致性", False, str(e)))
            return False
    
    async def test_large_batch(self):
        """测试 8: 大批量文本"""
        print("\n" + "="*60)
        print("测试 8: 大批量文本 Embedding (分批处理)")
        print("="*60)
        
        # 生成25个测试文本，会分3批处理（10+10+5）
        batch_size = 25
        test_texts = [f"This is test sentence number {i} for batch embedding." for i in range(batch_size)]
        
        print(f"测试文本数量: {batch_size}")
        print(f"将自动分批处理（每批最多10条）")
        
        try:
            embeddings = await self.service.embed_batch(test_texts)
            print(f"✅ 大批量 Embedding 生成成功")
            print(f"   生成数量: {len(embeddings)}")
            print(f"   向量维度: {len(embeddings[0])}")
            
            if len(embeddings) == batch_size:
                print(f"   ✅ 数量验证通过")
                self.test_results.append(("大批量embedding", True, None))
                return True
            else:
                print(f"   ⚠️  数量不匹配 (期望: {batch_size}, 实际: {len(embeddings)})")
                self.test_results.append(("大批量embedding", False, "数量不匹配"))
                return False
        except Exception as e:
            print(f"❌ 大批量 Embedding 生成失败: {e}")
            self.test_results.append(("大批量embedding", False, str(e)))
            return False
    
    def print_summary(self):
        """打印测试摘要"""
        print("\n" + "="*60)
        print("测试摘要")
        print("="*60)
        
        total = len(self.test_results)
        passed = sum(1 for _, success, _ in self.test_results if success)
        failed = total - passed
        
        print(f"\n总测试数: {total}")
        print(f"通过: {passed} ✅")
        print(f"失败: {failed} ❌")
        print(f"通过率: {(passed/total*100):.1f}%")
        
        if failed > 0:
            print("\n失败的测试:")
            for name, success, error in self.test_results:
                if not success:
                    print(f"  ❌ {name}: {error}")
        
        print("\n" + "="*60)


async def main():
    """主测试函数"""
    print("="*60)
    print("Embedding 服务测试")
    print("="*60)
    
    # 检查环境变量
    print("\n检查配置...")
    print(f"默认提供商: {settings.default_embedding_provider}")
    print(f"默认模型: {settings.default_embedding_model}")
    
    # 检查 API Key
    config = settings.get_embedding_config()
    if not config["api_key"]:
        print(f"\n❌ 错误: {settings.default_embedding_provider} API Key 未配置")
        print("请在 .env 文件中设置相应的 API Key")
        return
    
    print(f"✅ API Key 已配置")
    
    # 创建测试器
    tester = EmbeddingTester()
    
    # 运行所有测试
    await tester.test_initialization()
    
    if tester.service:  # 只有初始化成功后才继续其他测试
        await tester.test_single_embedding()
        await tester.test_batch_embedding()
        await tester.test_empty_input()
        await tester.test_chinese_text()
        await tester.test_long_text()
        await tester.test_dimension_consistency()
        await tester.test_large_batch()
    
    # 打印测试摘要
    tester.print_summary()


if __name__ == "__main__":
    asyncio.run(main())

