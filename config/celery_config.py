"""
Celery任务队列配置
"""

import os
from celery import Celery
from kombu import Exchange, Queue

# 从环境变量获取配置
broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# 创建Celery应用
app = Celery(
    'geo_promotion',
    broker=broker_url,
    backend=result_backend,
    include=[
        'src.tasks.optimization_tasks',
        'src.tasks.distribution_tasks',
        'src.tasks.monitoring_tasks'
    ]
)

# 配置选项
app.conf.update(
    # 任务序列化
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # 时区
    timezone='Asia/Shanghai',
    enable_utc=True,
    
    # 任务路由
    task_routes={
        'optimization_tasks.*': {'queue': 'optimization'},
        'distribution_tasks.*': {'queue': 'distribution'},
        'monitoring_tasks.*': {'queue': 'monitoring'},
        'product_promotion_tasks.*': {'queue': 'promotion'}
    },
    
    # 队列配置
    task_queues=(
        Queue('optimization', Exchange('optimization'), routing_key='optimization'),
        Queue('distribution', Exchange('distribution'), routing_key='distribution'),
        Queue('monitoring', Exchange('monitoring'), routing_key='monitoring'),
        Queue('promotion', Exchange('promotion'), routing_key='promotion'),
        Queue('default', Exchange('default'), routing_key='default'),
    ),
    
    # 任务默认队列
    task_default_queue='default',
    task_default_exchange='default',
    task_default_routing_key='default',
    
    # 任务执行限制
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # 重试策略
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # 结果过期时间
    result_expires=3600,  # 1小时
    
    # 监控配置
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # 日志配置
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s'
)

# 定时任务配置
app.conf.beat_schedule = {
    # 每5分钟检查一次待处理任务
    'check-pending-tasks': {
        'task': 'monitoring_tasks.check_pending_tasks',
        'schedule': 300.0,  # 5分钟
        'options': {'queue': 'monitoring'}
    },
    
    # 每小时执行一次性能监控
    'performance-monitoring': {
        'task': 'monitoring_tasks.performance_monitoring',
        'schedule': 3600.0,  # 1小时
        'options': {'queue': 'monitoring'}
    },
    
    # 每天执行一次竞品分析
    'competitor-analysis': {
        'task': 'monitoring_tasks.competitor_analysis',
        'schedule': 86400.0,  # 24小时
        'options': {'queue': 'monitoring'}
    },
    
    # 每30分钟清理过期任务结果
    'cleanup-expired-results': {
        'task': 'monitoring_tasks.cleanup_expired_results',
        'schedule': 1800.0,  # 30分钟
        'options': {'queue': 'monitoring'}
    },
    
    # 每15分钟检查平台状态
    'check-platform-status': {
        'task': 'distribution_tasks.check_platform_status',
        'schedule': 900.0,  # 15分钟
        'options': {'queue': 'distribution'}
    },
    
    # 每10分钟批量处理优化任务
    'batch-optimization': {
        'task': 'optimization_tasks.process_batch_optimization',
        'schedule': 600.0,  # 10分钟
        'options': {'queue': 'optimization'}
    },
    
    # 每20分钟批量处理分发任务
    'batch-distribution': {
        'task': 'distribution_tasks.process_batch_distribution',
        'schedule': 1200.0,  # 20分钟
        'options': {'queue': 'distribution'}
    },
    
    # 每天生成性能报告
    'generate-daily-report': {
        'task': 'monitoring_tasks.generate_daily_report',
        'schedule': 86400.0,  # 24小时
        'options': {'queue': 'monitoring'}
    }
}

# 任务错误处理配置
app.conf.task_annotations = {
    '*': {
        'rate_limit': '10/m',  # 默认速率限制
        'max_retries': 3,
        'default_retry_delay': 60,  # 60秒重试延迟
        'retry_backoff': True,
        'retry_backoff_max': 600,  # 最大10分钟
        'retry_jitter': True
    },
    'optimization_tasks.*': {
        'rate_limit': '5/m',  # 优化任务速率限制
        'max_retries': 2,
        'default_retry_delay': 30
    },
    'distribution_tasks.*': {
        'rate_limit': '20/m',  # 分发任务速率限制
        'max_retries': 5,
        'default_retry_delay': 120
    }
}

# 任务优先级配置
app.conf.task_default_priority = 5
app.conf.task_queue_max_priority = 10

# 导入任务模块
if __name__ == '__main__':
    app.start()