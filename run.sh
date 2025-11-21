#!/bin/bash

# PaperWhisperer 启动脚本

set -e

echo "======================================"
echo "  PaperWhisperer 启动脚本"
echo "======================================"

# 检查配置（优先使用环境变量，其次是 .env 文件）
if [ -f .env ]; then
    echo "✓ 找到配置文件 .env"
elif [ -n "$QWEN_API_KEY" ] || [ -n "$OPENAI_API_KEY" ] || [ -n "$DEEPSEEK_API_KEY" ]; then
    echo "✓ 检测到环境变量中的 API Key"
else
    echo "错误: 未找到配置"
    echo ""
    echo "请选择以下任一配置方式："
    echo "  1. 使用环境变量（推荐）："
    echo "     export QWEN_API_KEY=your-key"
    echo "     export MINERU_TOKEN=your-token"
    echo ""
    echo "  2. 创建 .env 文件："
    echo "     cp .env.example .env"
    echo "     然后编辑 .env 文件填写配置"
    echo ""
    exit 1
fi

# 检查必需的配置
if [ -z "$MINERU_TOKEN" ]; then
    echo "警告: 未配置 MINERU_TOKEN，PDF 解析功能将不可用"
fi

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "错误: 未安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "错误: 未安装 Docker Compose"
    exit 1
fi

echo "✓ Docker 环境检查通过"

# 创建必要的目录
echo "创建数据目录..."
mkdir -p data/uploads data/parsed data/embeddings data/summaries logs

# 启动服务
echo ""
echo "正在启动服务..."
docker-compose up -d

echo ""
echo "======================================"
echo "  PaperWhisperer 已启动！"
echo "======================================"
echo ""
echo "服务地址:"
echo "  - 前端: http://localhost"
echo "  - 后端 API: http://localhost:8000"
echo "  - API 文档: http://localhost:8000/docs"
echo "  - Milvus: localhost:19530"
echo "  - MinIO 控制台: http://localhost:9001"
echo ""
echo "查看日志:"
echo "  docker-compose logs -f"
echo ""
echo "停止服务:"
echo "  docker-compose down"
echo ""

