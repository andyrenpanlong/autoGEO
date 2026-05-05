"""
日志配置工具
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
import json
from datetime import datetime

from src.config import settings

def setup_logger(name: str = None) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger(name or __name__)
    
    # 如果已经配置过，直接返回
    if logger.handlers:
        return logger
    
    # 设置日志级别
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # 创建日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（如果配置了日志文件）
    if settings.LOG_FILE:
        try:
            # 确保日志目录存在
            log_path = Path(settings.LOG_FILE)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 创建轮转文件处理器
            file_handler = RotatingFileHandler(
                settings.LOG_FILE,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
        except Exception as e:
            logger.warning(f"无法创建文件日志处理器: {str(e)}")
    
    # JSON格式处理器（用于结构化日志）
    if settings.APP_ENV == "production":
        try:
            json_handler = JSONLogHandler()
            json_handler.setLevel(log_level)
            logger.addHandler(json_handler)
        except Exception as e:
            logger.warning(f"无法创建JSON日志处理器: {str(e)}")
    
    return logger

class JSONLogHandler(logging.Handler):
    """JSON格式日志处理器"""
    
    def __init__(self):
        super().__init__()
    
    def emit(self, record):
        """发出日志记录"""
        try:
            log_entry = self._format_record(record)
            print(json.dumps(log_entry, ensure_ascii=False))
        except Exception:
            self.handleError(record)
    
    def _format_record(self, record):
        """格式化日志记录为JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # 添加异常信息
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # 添加额外字段
        if hasattr(record, 'extra'):
            log_entry.update(record.extra)
        
        return log_entry

def get_request_logger():
    """获取请求日志记录器"""
    return setup_logger("request")

def get_database_logger():
    """获取数据库日志记录器"""
    return setup_logger("database")

def get_monitoring_logger():
    """获取监控日志记录器"""
    return setup_logger("monitoring")

def get_task_logger():
    """获取任务日志记录器"""
    return setup_logger("task")

# 预定义的日志记录器
request_logger = get_request_logger()
database_logger = get_database_logger()
monitoring_logger = get_monitoring_logger()
task_logger = get_task_logger()

# 导出
__all__ = [
    "setup_logger",
    "request_logger",
    "database_logger", 
    "monitoring_logger",
    "task_logger"
]