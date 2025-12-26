#!/bin/bash
# 使用正确的 Python 环境运行测试

echo "============================================================"
echo "PaperWhisperer - 测试运行器（使用 rag-agent 环境）"
echo "============================================================"
echo ""

# 使用 rag-agent 环境的 Python
PYTHON_BIN="/opt/miniconda3/envs/rag-agent/bin/python"

# 检查 Python 版本
echo "Python 版本:"
$PYTHON_BIN --version
echo ""

# 检查 pymilvus 是否已安装
echo "检查 pymilvus:"
if $PYTHON_BIN -c "import pymilvus; print(f'✅ pymilvus {pymilvus.__version__} 已安装')" 2>/dev/null; then
    echo ""
else
    echo "❌ pymilvus 未安装"
    echo "正在安装..."
    $PYTHON_BIN -m pip install pymilvus==2.3.3
    echo ""
fi

# 检查 pytest
echo "检查 pytest:"
if $PYTHON_BIN -c "import pytest; print(f'✅ pytest {pytest.__version__} 已安装')" 2>/dev/null; then
    echo ""
else
    echo "❌ pytest 未安装"
    echo "正在安装..."
    $PYTHON_BIN -m pip install pytest pytest-asyncio pytest-mock
    echo ""
fi

echo "============================================================"
echo "🚀 开始运行测试..."
echo "============================================================"
echo ""

# 运行测试
cd "$(dirname "$0")"
$PYTHON_BIN -m pytest test_milvus_service.py -v "$@"

