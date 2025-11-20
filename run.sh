#!/bin/bash

# PaperWhisperer 启动脚本

set -e

echo "======================================"
echo "  PaperWhisperer 启动脚本"
echo "======================================"

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "错误: 未找到 .env 文件"
    echo "请复制 .env.example 为 .env 并填写配置"
    echo "  cp .env.example .env"
    exit 1
fi

echo "✓ 找到配置文件 .env"

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

