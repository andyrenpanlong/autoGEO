"""
内容分发API路由
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
import uuid
import time

from src.services.distribution_service import DistributionService, distribution_service
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

# 请求/响应模型
class DistributionRequest(BaseModel):
    """分发请求"""
    content: str = Field(..., description="要分发的内容", min_length=10, max_length=10000)
    content_id: str = Field(..., description="内容ID")
    metadata: dict = Field(
        default_factory=dict, 
        description="元数据"
    )
    platforms: List[str] = Field(
        default_factory=lambda: ["deepseek", "doubao"],
        description="目标平台列表"
    )
    distribute_in_background: bool = Field(
        default=False, 
        description="是否在后台分发"
    )

class DistributionResponse(BaseModel):
    """分发响应"""
    request_id: str = Field(..., description="请求ID")
    content_id: str = Field(..., description="内容ID")
    status: str = Field(..., description="状态")
    distribution_results: List[dict] = Field(default_factory=list, description="分发结果")
    total_platforms: int = Field(..., description="目标平台总数")
    successful: int = Field(..., description="成功数")
    failed: int = Field(..., description="失败数")
    processing_time: Optional[float] = Field(None, description="处理时间（秒）")

class BatchDistributionRequest(BaseModel):
    """批量分发请求"""
    contents: List[dict] = Field(
        ..., 
        description="内容列表，每个元素包含content和metadata",
        min_items=1, 
        max_items=50
    )
    platforms: List[str] = Field(
        default_factory=lambda: ["deepseek", "doubao"],
        description="目标平台列表"
    )

class BatchDistributionResponse(BaseModel):
    """批量分发响应"""
    request_id: str = Field(..., description="请求ID")
    status: str = Field(..., description="状态")
    results: List[DistributionResponse] = Field(default_factory=list, description="分发结果")
    total_contents: int = Field(..., description="内容总数")
    total_successful: int = Field(..., description="总成功数")
    total_failed: int = Field(..., description="总失败数")
    total_processing_time: float = Field(..., description="总处理时间")

class PlatformStatusResponse(BaseModel):
    """平台状态响应"""
    platforms: dict = Field(..., description="平台状态信息")
    total_configured: int = Field(..., description="已配置平台数")
    total_available: int = Field(..., description="可用平台数")

# 分发任务存储
distribution_tasks = {}

@router.post("/", response_model=DistributionResponse)
async def distribute_content(
    request: DistributionRequest,
    background_tasks: BackgroundTasks,
    distributor: DistributionService = Depends(lambda: distribution_service)
):
    """
    分发内容到AI平台
    
    将优化后的内容分发到指定的AI平台，提高内容可见性
    """
    request_id = str(uuid.uuid4())
    
    logger.info(f"收到分发请求 {request_id}: 内容 {request.content_id} 到 {len(request.platforms)} 个平台")
    
    if request.distribute_in_background:
        # 后台分发
        background_tasks.add_task(
            _process_distribution_background,
            request_id, request, distributor
        )
        
        return DistributionResponse(
            request_id=request_id,
            content_id=request.content_id,
            status="processing",
            distribution_results=[],
            total_platforms=len(request.platforms),
            successful=0,
            failed=0,
            processing_time=None
        )
    else:
        # 同步分发
        return await _process_distribution_sync(request_id, request, distributor)

@router.post("/batch", response_model=BatchDistributionResponse)
async def batch_distribute_content(
    request: BatchDistributionRequest,
    distributor: DistributionService = Depends(lambda: distribution_service)
):
    """
    批量分发内容
    
    同时分发多个内容到AI平台，提高处理效率
    """
    request_id = str(uuid.uuid4())
    
    logger.info(f"收到批量分发请求 {request_id}: {len(request.contents)} 个内容")
    
    start_time = time.time()
    
    try:
        # 准备分发数据
        contents = []
        metadata_list = []
        
        for item in request.contents:
            contents.append(item.get("content", ""))
            metadata_list.append(item.get("metadata", {}))
        
        # 批量分发
        batch_results = await distributor.distribute_batch(
            contents=contents,
            metadata_list=metadata_list,
            platform_names=request.platforms
        )
        
        end_time = time.time()
        total_processing_time = end_time - start_time
        
        # 构建响应
        distribution_responses = []
        total_successful = 0
        total_failed = 0
        
        for i, platform_results in enumerate(batch_results):
            content_id = metadata_list[i].get("content_id", f"content_{i}")
            
            successful = sum(1 for r in platform_results if r.success)
            failed = len(platform_results) - successful
            
            total_successful += successful
            total_failed += failed
            
            distribution_responses.append(
                DistributionResponse(
                    request_id=str(uuid.uuid4()),
                    content_id=content_id,
                    status="completed",
                    distribution_results=[
                        {
                            "platform": r.platform,
                            "success": r.success,
                            "content_id": r.content_id,
                            "error_message": r.error_message,
                            "timestamp": r.timestamp
                        }
                        for r in platform_results
                    ],
                    total_platforms=len(platform_results),
                    successful=successful,
                    failed=failed,
                    processing_time=None  # 单个处理时间在批量中不单独计算
                )
            )
        
        return BatchDistributionResponse(
            request_id=request_id,
            status="completed",
            results=distribution_responses,
            total_contents=len(request.contents),
            total_successful=total_successful,
            total_failed=total_failed,
            total_processing_time=total_processing_time
        )
        
    except Exception as e:
        logger.error(f"批量分发失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"批量分发失败: {str(e)}"
        )

@router.get("/platforms", response_model=PlatformStatusResponse)
async def get_platform_status(
    distributor: DistributionService = Depends(lambda: distribution_service)
):
    """
    获取平台状态
    
    查询所有配置的AI平台状态和可用性
    """
    try:
        # 确保分发服务已初始化
        if not distributor.initialized:
            await distributor.initialize()
        
        platform_status = await distributor.get_platform_status()
        
        # 统计信息
        total_configured = len(platform_status)
        total_available = sum(
            1 for status in platform_status.values() 
            if status.get("configured", False)
        )
        
        return PlatformStatusResponse(
            platforms=platform_status,
            total_configured=total_configured,
            total_available=total_available
        )
        
    except Exception as e:
        logger.error(f"获取平台状态失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取平台状态失败: {str(e)}"
        )

@router.get("/task/{task_id}")
async def get_distribution_task_status(task_id: str):
    """
    获取分发任务状态
    
    查询后台分发任务的状态和结果
    """
    if task_id not in distribution_tasks:
        raise HTTPException(
            status_code=404,
            detail=f"分发任务 {task_id} 不存在"
        )
    
    task_info = distribution_tasks[task_id]
    
    return {
        "task_id": task_id,
        "status": task_info.get("status", "unknown"),
        "content_id": task_info.get("content_id"),
        "platforms": task_info.get("platforms", []),
        "created_at": task_info.get("created_at"),
        "updated_at": task_info.get("updated_at"),
        "results": task_info.get("results"),
        "error": task_info.get("error")
    }

@router.post("/test/{platform}")
async def test_platform_connection(
    platform: str,
    distributor: DistributionService = Depends(lambda: distribution_service)
):
    """
    测试平台连接
    
    测试指定AI平台的连接和可用性
    """
    try:
        # 确保分发服务已初始化
        if not distributor.initialized:
            await distributor.initialize()
        
        # 检查平台是否配置
        platform_status = await distributor.get_platform_status()
        
        if platform not in platform_status:
            raise HTTPException(
                status_code=404,
                detail=f"平台 {platform} 未配置"
            )
        
        if not platform_status[platform].get("configured", False):
            raise HTTPException(
                status_code=400,
                detail=f"平台 {platform} API密钥未配置"
            )
        
        # 测试连接（这里简化处理，实际需要调用平台API）
        test_content = "这是一个测试内容，用于验证平台连接。"
        test_metadata = {
            "test": True,
            "timestamp": time.time(),
            "content_id": f"test_{int(time.time())}"
        }
        
        # 这里应该调用实际的分发方法，但为了安全，我们只模拟
        # 实际应用中应该调用 distributor.distribute_to_platforms
        
        return {
            "platform": platform,
            "status": "available",
            "tested_at": time.time(),
            "message": f"平台 {platform} 连接测试通过（模拟）",
            "note": "实际连接测试需要调用平台API，这里仅检查配置"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"平台连接测试失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"平台连接测试失败: {str(e)}"
        )

# 辅助函数
async def _process_distribution_sync(
    request_id: str,
    request: DistributionRequest,
    distributor: DistributionService
) -> DistributionResponse:
    """同步处理分发"""
    start_time = time.time()
    
    try:
        # 确保分发服务已初始化
        if not distributor.initialized:
            await distributor.initialize()
        
        # 执行分发
        results = await distributor.distribute_to_platforms(
            content=request.content,
            metadata=request.metadata,
            platform_names=request.platforms
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 统计结果
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        return DistributionResponse(
            request_id=request_id,
            content_id=request.content_id,
            status="completed",
            distribution_results=[
                {
                    "platform": r.platform,
                    "success": r.success,
                    "content_id": r.content_id,
                    "error_message": r.error_message,
                    "timestamp": r.timestamp
                }
                for r in results
            ],
            total_platforms=len(results),
            successful=successful,
            failed=failed,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"分发失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"分发失败: {str(e)}"
        )

async def _process_distribution_background(
    request_id: str,
    request: DistributionRequest,
    distributor: DistributionService
):
    """后台处理分发"""
    from datetime import datetime
    
    task_info = {
        "request_id": request_id,
        "content_id": request.content_id,
        "platforms": request.platforms,
        "status": "processing",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "results": None,
        "error": None
    }
    
    distribution_tasks[request_id] = task_info
    
    try:
        start_time = time.time()
        
        # 确保分发服务已初始化
        if not distributor.initialized:
            await distributor.initialize()
        
        # 执行分发
        results = await distributor.distribute_to_platforms(
            content=request.content,
            metadata=request.metadata,
            platform_names=request.platforms
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 统计结果
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        task_info["status"] = "completed"
        task_info["updated_at"] = datetime.now().isoformat()
        task_info["results"] = {
            "distribution_results": [
                {
                    "platform": r.platform,
                    "success": r.success,
                    "content_id": r.content_id
                }
                for r in results
            ],
            "total_platforms": len(results),
            "successful": successful,
            "failed": failed,
            "processing_time": processing_time
        }
        
        logger.info(f"���台分发任务 {request_id} 完成: {successful} 成功, {failed} 失败")
        
    except Exception as e:
        task_info["status"] = "failed"
        task_info["updated_at"] = datetime.now().isoformat()
        task_info["error"] = str(e)
        
        logger.error(f"后台分发任务 {request_id} 失败: {str(e)}")