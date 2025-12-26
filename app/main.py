"""
FastAPI 主应用入口
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

# .env 文件已在 app.config 模块中自动加载
from app.config import settings
from app.utils.logger import log
from app.routers import upload, translate, summary, chat
from app.services.milvus_service import milvus_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    log.info("=" * 50)
    log.info("PaperWhisperer 正在启动...")
    log.info(f"环境: {'开发' if settings.debug else '生产'}")
    log.info(f"日志级别: {settings.log_level}")
    log.info(f"默认 LLM 提供商: {settings.default_llm_provider}")
    log.info(f"默认 Embedding 提供商: {settings.default_embedding_provider}")
    log.info("=" * 50)
    
    # 预连接 Milvus（可选，失败不影响启动）
    try:
        await milvus_service.connect()
        log.info("Milvus 预连接成功")
    except Exception as e:
        log.warning(f"Milvus 预连接失败（将在首次使用时重试）: {e}")
    
    yield
    
    # 关闭时执行
    log.info("PaperWhisperer 正在关闭...")
    
    # 断开 Milvus 连接
    try:
        await milvus_service.disconnect()
    except Exception as e:
        log.warning(f"Milvus 断开连接失败: {e}")


# 创建 FastAPI 应用
app = FastAPI(
    title="PaperWhisperer",
    description="智能论文助手 - 解析、翻译、摘要、对话",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需要限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    log.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "内部服务器错误",
            "detail": str(exc) if settings.debug else "请联系管理员"
        }
    )


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "PaperWhisperer",
        "version": "1.0.0"
    }


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用 PaperWhisperer - 智能论文助手",
        "docs": "/docs",
        "health": "/health"
    }


# 注册路由
app.include_router(upload.router, prefix="/api", tags=["上传与解析"])
app.include_router(translate.router, prefix="/api", tags=["翻译"])
app.include_router(summary.router, prefix="/api", tags=["摘要"])
app.include_router(chat.router, prefix="/api", tags=["对话"])

# 挂载静态文件服务，用于提供论文中的图片
# 图片路径格式: /api/images/{paper_id}/images/xxx.jpg
app.mount("/api/images", StaticFiles(directory=str(settings.parsed_dir)), name="paper_images")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.backend_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

