"""
应用配置管理
"""

import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Settings(BaseSettings):
    """应用设置"""
    
    # 应用设置
    APP_NAME: str = "GEO Promotion Backend"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # 服务器设置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库设置
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/geo_promotion"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # CORS设置
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    # API密钥
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_AI_API_KEY: Optional[str] = None
    PERPLEXITY_API_KEY: Optional[str] = None
    
    # 国内平台API密钥
    DEEPSEEK_API_KEY: Optional[str] = None
    DOUBAO_API_KEY: Optional[str] = None
    KIMI_API_KEY: Optional[str] = None
    TONGYI_API_KEY: Optional[str] = None
    
    # GEO优化设置
    GEO_OPTIMIZATION_STRATEGY: str = "authoritative_rewrite"
    MAX_CONTENT_LENGTH: int = 3000
    MIN_CITATION_COUNT: int = 3
    OPTIMIZATION_THRESHOLD: float = 0.7
    
    # 监控设置
    MONITORING_INTERVAL: int = 3600  # 秒
    CITATION_CHECK_INTERVAL: int = 86400  # 24小时
    
    # 日志设置
    LOG_LEVEL: str = "info"
    LOG_FILE: str = "logs/geo_promotion.log"
    
    # 任务队列设置
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # 向量数据库设置
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # 速率限制
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # 缓存设置
    CACHE_TTL: int = 300  # 5分钟
    CACHE_MAX_SIZE: int = 1000
    
    # 安全设置
    JWT_SECRET_KEY: str = "your-jwt-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 外部服务
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_PORT: int = 9090
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 创建全局设置实例
settings = Settings()

# 导出设置
__all__ = ["settings"]