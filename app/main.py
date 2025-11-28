"""
FastAPI 主应用入口
"""
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

# 尝试加载 .env 文件（如果存在）
from dotenv import load_dotenv
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    try:
        load_dotenv(env_file)
    except (PermissionError, OSError):
        # .env 文件存在但不可读，忽略并使用环境变量
        pass

from app.config import settings
from app.utils.logger import log
from app.routers import upload, translate, summary, chat


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
    
    yield
    
    # 关闭时执行
    log.info("PaperWhisperer 正在关闭...")


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


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.backend_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

