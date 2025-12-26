#!/bin/bash
# Milvus 测试运行脚本
# 
# 用法：
#   ./run_milvus_tests.sh          - 运行所有测试
#   ./run_milvus_tests.sh unit     - 只运行单元测试
#   ./run_milvus_tests.sh integration - 只运行集成测试

set -e

# 确保在正确的目录
cd "$(dirname "$0")"

# 激活 conda 环境
echo "🔄 激活 paper-whisperer 环境..."
eval "$(conda shell.bash hook)"
conda activate paper-whisperer

# 设置本地测试的 Milvus 主机
export MILVUS_HOST=localhost

echo ""
echo "========================================"
echo "  Milvus 服务测试"
echo "========================================"
echo ""

case "${1:-all}" in
    unit)
        echo "📝 运行单元测试（使用 Mock，不需要真实服务）..."
        python -m pytest test_milvus_service.py -v -m "not integration"
        ;;
    integration)
        echo "🔌 运行集成测试（需要 Milvus 服务）..."
        echo ""
        echo "检查 Milvus 服务状态..."
        if docker-compose ps milvus | grep -q "healthy"; then
            echo "✅ Milvus 服务正常运行"
            python -m pytest test_milvus_service.py -v -m integration
        else
            echo "❌ Milvus 服务未运行"
            echo "请先启动 Milvus："
            echo "  docker-compose up -d milvus"
            exit 1
        fi
        ;;
    all|*)
        echo "🧪 运行所有测试..."
        python -m pytest test_milvus_service.py -v
        ;;
esac

echo ""
echo "========================================"
echo "  测试完成！"
echo "========================================"

