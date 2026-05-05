"""
GEO Promotion Backend - 主应用入口
基于GEO技术的产品推广优化系统
"""

import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from src.database import init_db, get_db
from src.routers import optimize, distribute, monitor, analyze, admin
from src.middleware import logging_middleware, rate_limit_middleware
from src.utils.logger import setup_logger
from src.config import settings

# 加载环境变量
load_dotenv()

# 设置日志
logger = setup_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    # 启动时
    logger.info("Starting GEO Promotion Backend...")
    
    # 初始化数据库
    await init_db()
    logger.info("Database initialized successfully")
    
    # 初始化向量数据库
    from src.services.vector_store import init_vector_store
    await init_vector_store()
    logger.info("Vector store initialized successfully")
    
    # 启动监控任务
    from src.tasks.monitor import start_monitoring_tasks
    await start_monitoring_tasks()
    logger.info("Monitoring tasks started")
    
    yield
    
    # 关闭时
    logger.info("Shutting down GEO Promotion Backend...")
    # 清理资源

# 创建FastAPI应用
app = FastAPI(
    title="GEO Promotion Backend",
    description="基于GEO技术的产品推广优化系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# 自定义中间件
app.middleware("http")(logging_middleware)
app.middleware("http")(rate_limit_middleware)

# 注册路由
app.include_router(optimize.router, prefix="/api/v1/optimize", tags=["内容优化"])
app.include_router(distribute.router, prefix="/api/v1/distribute", tags=["内容分发"])
app.include_router(monitor.router, prefix="/api/v1/monitor", tags=["效果监控"])
app.include_router(analyze.router, prefix="/api/v1/analyze", tags=["数据分析"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["管理后台"])

# 健康检查端点
@app.get("/")
async def root():
    """根端点"""
    return {
        "message": "GEO Promotion Backend API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "database": "connected",
        "vector_store": "ready",
        "monitoring": "active"
    }

@app.get("/metrics")
async def metrics():
    """Prometheus指标端点"""
    # 这里可以集成Prometheus客户端
    return {"metrics": "available"}

# 错误处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理"""
    logger.error(f"HTTP error: {exc.detail}")
    return {
        "error": exc.detail,
        "status_code": exc.status_code
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理"""
    logger.error(f"Unexpected error: {str(exc)}")
    return {
        "error": "Internal server error",
        "detail": str(exc) if settings.APP_DEBUG else "An unexpected error occurred"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.APP_DEBUG,
        log_level=settings.LOG_LEVEL
    )