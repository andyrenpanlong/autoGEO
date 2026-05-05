"""
内容优化API路由
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
import uuid

from src.services.geo_optimizer import GEOOptimizer, OptimizationStrategy
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

# 请求/响应模型
class ProductInfo(BaseModel):
    """产品信息"""
    name: str = Field(..., description="产品名称")
    description: str = Field(..., description="产品描述")
    category: str = Field(..., description="产品类别")
    features: List[str] = Field(default_factory=list, description="产品特点")
    keywords: List[str] = Field(default_factory=list, description="关键词")
    statistics: Optional[dict] = Field(None, description="统计数据")
    target_audience: Optional[str] = Field(None, description="目标受众")
    brand: Optional[str] = Field(None, description="品牌")

class OptimizationRequest(BaseModel):
    """优化请求"""
    content: str = Field(..., description="原始内容", min_length=10, max_length=10000)
    product_info: ProductInfo = Field(..., description="产品信息")
    target_platforms: List[str] = Field(
        default=["general"], 
        description="目标平台"
    )
    strategies: List[str] = Field(
        default_factory=lambda: ["authoritative_rewrite", "statistical_enhancement"],
        description="优化策略"
    )
    optimize_in_background: bool = Field(
        default=False, 
        description="是否在后台优化"
    )

class OptimizationResponse(BaseModel):
    """优化响应"""
    request_id: str = Field(..., description="请求ID")
    status: str = Field(..., description="状态")
    original_content: str = Field(..., description="原始内容")
    optimized_content: Optional[str] = Field(None, description="优化后内容")
    strategy_used: List[str] = Field(default_factory=list, description="使用的策略")
    confidence_score: float = Field(..., description="置信度分数")
    changes_made: List[dict] = Field(default_factory=list, description="所做的更改")
    metadata: dict = Field(default_factory=dict, description="元数据")
    processing_time: Optional[float] = Field(None, description="处理时间（秒）")

class BatchOptimizationRequest(BaseModel):
    """批量优化请求"""
    contents: List[str] = Field(..., description="内容列表", min_items=1, max_items=100)
    product_info: ProductInfo = Field(..., description="产品信息")
    target_platforms: List[str] = Field(
        default=["general"], 
        description="目标平台"
    )

class BatchOptimizationResponse(BaseModel):
    """批量优化响应"""
    request_id: str = Field(..., description="请求ID")
    status: str = Field(..., description="状态")
    results: List[OptimizationResponse] = Field(default_factory=list, description="优化结果")
    total_processed: int = Field(..., description="处理总数")
    successful: int = Field(..., description="成功数")
    failed: int = Field(..., description="失败数")
    total_processing_time: float = Field(..., description="总处理时间")

# 依赖项
def get_geo_optimizer():
    """获取GEO优化器实例"""
    return GEOOptimizer()

# 优化任务存储（简化版，实际应用中应使用数据库）
optimization_tasks = {}

@router.post("/", response_model=OptimizationResponse)
async def optimize_content(
    request: OptimizationRequest,
    background_tasks: BackgroundTasks,
    optimizer: GEOOptimizer = Depends(get_geo_optimizer)
):
    """
    优化单个内容
    
    根据GEO策略优化产品推广内容，提高AI引用率
    """
    request_id = str(uuid.uuid4())
    
    logger.info(f"收到优化请求 {request_id}: {request.product_info.name}")
    
    if request.optimize_in_background:
        # 后台优化
        background_tasks.add_task(
            _process_optimization_background,
            request_id, request, optimizer
        )
        
        return OptimizationResponse(
            request_id=request_id,
            status="processing",
            original_content=request.content,
            optimized_content=None,
            strategy_used=[],
            confidence_score=0.0,
            changes_made=[],
            metadata={"message": "优化任务已提交到后台处理"}
        )
    else:
        # 同步优化
        return await _process_optimization_sync(request_id, request, optimizer)

@router.post("/batch", response_model=BatchOptimizationResponse)
async def batch_optimize_content(
    request: BatchOptimizationRequest,
    optimizer: GEOOptimizer = Depends(get_geo_optimizer)
):
    """
    批量优化内容
    
    同时优化多个内容，提高处理效率
    """
    request_id = str(uuid.uuid4())
    
    logger.info(f"收到批量优化请求 {request_id}: {len(request.contents)} 个内容")
    
    import time
    start_time = time.time()
    
    try:
        # 转换策略
        strategies = [
            OptimizationStrategy.AUTHORITATIVE_REWRITE,
            OptimizationStrategy.STATISTICAL_ENHANCEMENT,
            OptimizationStrategy.CITATION_OPTIMIZATION
        ]
        
        # 批量优化
        results = await optimizer.batch_optimize(
            contents=request.contents,
            product_info=request.product_info.dict(),
            target_platforms=request.target_platforms
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 构建响应
        optimization_responses = []
        successful = 0
        failed = 0
        
        for result in results:
            if hasattr(result, 'optimized_content'):
                optimization_responses.append(
                    OptimizationResponse(
                        request_id=str(uuid.uuid4()),
                        status="completed",
                        original_content=result.original_content,
                        optimized_content=result.optimized_content,
                        strategy_used=result.strategy_used,
                        confidence_score=result.confidence_score,
                        changes_made=result.changes_made,
                        metadata=result.metadata
                    )
                )
                successful += 1
            else:
                failed += 1
        
        return BatchOptimizationResponse(
            request_id=request_id,
            status="completed",
            results=optimization_responses,
            total_processed=len(request.contents),
            successful=successful,
            failed=failed,
            total_processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"批量优化失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"批量优化失败: {str(e)}"
        )

@router.get("/strategies")
async def get_available_strategies():
    """
    获取可用的优化策略
    
    返回系统支持的所有GEO优化策略
    """
    strategies = [
        {
            "id": strategy.value,
            "name": _get_strategy_name(strategy),
            "description": _get_strategy_description(strategy),
            "recommended_for": _get_strategy_recommendations(strategy)
        }
        for strategy in OptimizationStrategy
    ]
    
    return {
        "strategies": strategies,
        "count": len(strategies)
    }

@router.get("/task/{task_id}")
async def get_optimization_task_status(task_id: str):
    """
    获取优化任务状态
    
    查询后台优化任务的状态和结果
    """
    if task_id not in optimization_tasks:
        raise HTTPException(
            status_code=404,
            detail=f"任务 {task_id} 不存在"
        )
    
    task_info = optimization_tasks[task_id]
    
    return {
        "task_id": task_id,
        "status": task_info.get("status", "unknown"),
        "created_at": task_info.get("created_at"),
        "updated_at": task_info.get("updated_at"),
        "result": task_info.get("result"),
        "error": task_info.get("error")
    }

# 辅助函数
async def _process_optimization_sync(
    request_id: str,
    request: OptimizationRequest,
    optimizer: GEOOptimizer
) -> OptimizationResponse:
    """同步处理优化"""
    import time
    start_time = time.time()
    
    try:
        # 转换策略
        strategies = [
            OptimizationStrategy(s) for s in request.strategies
            if s in [s.value for s in OptimizationStrategy]
        ]
        
        if not strategies:
            strategies = [
                OptimizationStrategy.AUTHORITATIVE_REWRITE,
                OptimizationStrategy.STATISTICAL_ENHANCEMENT
            ]
        
        # 执行优化
        result = await optimizer.optimize_content(
            content=request.content,
            product_info=request.product_info.dict(),
            target_platforms=request.target_platforms,
            strategies=strategies
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        return OptimizationResponse(
            request_id=request_id,
            status="completed",
            original_content=result.original_content,
            optimized_content=result.optimized_content,
            strategy_used=result.strategy_used,
            confidence_score=result.confidence_score,
            changes_made=result.changes_made,
            metadata=result.metadata,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"优化失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"优化失败: {str(e)}"
        )

async def _process_optimization_background(
    request_id: str,
    request: OptimizationRequest,
    optimizer: GEOOptimizer
):
    """后台处理优化"""
    import time
    from datetime import datetime
    
    task_info = {
        "request_id": request_id,
        "status": "processing",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "result": None,
        "error": None
    }
    
    optimization_tasks[request_id] = task_info
    
    try:
        start_time = time.time()
        
        # 转换策略
        strategies = [
            OptimizationStrategy(s) for s in request.strategies
            if s in [s.value for s in OptimizationStrategy]
        ]
        
        if not strategies:
            strategies = [
                OptimizationStrategy.AUTHORITATIVE_REWRITE,
                OptimizationStrategy.STATISTICAL_ENHANCEMENT
            ]
        
        # 执行优化
        result = await optimizer.optimize_content(
            content=request.content,
            product_info=request.product_info.dict(),
            target_platforms=request.target_platforms,
            strategies=strategies
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        task_info["status"] = "completed"
        task_info["updated_at"] = datetime.now().isoformat()
        task_info["result"] = {
            "optimized_content": result.optimized_content,
            "strategy_used": result.strategy_used,
            "confidence_score": result.confidence_score,
            "processing_time": processing_time
        }
        
        logger.info(f"后台优化任务 {request_id} 完成")
        
    except Exception as e:
        task_info["status"] = "failed"
        task_info["updated_at"] = datetime.now().isoformat()
        task_info["error"] = str(e)
        
        logger.error(f"后台优化任务 {request_id} 失败: {str(e)}")

def _get_strategy_name(strategy: OptimizationStrategy) -> str:
    """获取策略名称"""
    names = {
        OptimizationStrategy.AUTHORITATIVE_REWRITE: "权威性重写",
        OptimizationStrategy.STATISTICAL_ENHANCEMENT: "统计增强",
        OptimizationStrategy.CITATION_OPTIMIZATION: "引用优化",
        OptimizationStrategy.STRUCTURAL_OPTIMIZATION: "结构优化",
        OptimizationStrategy.KEYWORD_STRATEGY: "关键词策略",
        OptimizationStrategy.MULTIMODAL_ENHANCEMENT: "多模态增强"
    }
    return names.get(strategy, strategy.value)

def _get_strategy_description(strategy: OptimizationStrategy) -> str:
    """获取策略描述"""
    descriptions = {
        OptimizationStrategy.AUTHORITATIVE_REWRITE: "增加内容的权威性和可信度，提高AI引用概率",
        OptimizationStrategy.STATISTICAL_ENHANCEMENT: "添加统计数据和证据支持，增强说服力",
        OptimizationStrategy.CITATION_OPTIMIZATION: "优化引用和来源，提高内容可信度",
        OptimizationStrategy.STRUCTURAL_OPTIMIZATION: "改善内容结构和组织，提高可读性",
        OptimizationStrategy.KEYWORD_STRATEGY: "优化关键词使用，提高搜索相关性",
        OptimizationStrategy.MULTIMODAL_ENHANCEMENT: "添加多模态元素描述，丰富内容形式"
    }
    return descriptions.get(strategy, "")

def _get_strategy_recommendations(strategy: OptimizationStrategy) -> List[str]:
    """获取策略推荐使用场景"""
    recommendations = {
        OptimizationStrategy.AUTHORITATIVE_REWRITE: ["技术文档", "行业报告", "专业指南"],
        OptimizationStrategy.STATISTICAL_ENHANCEMENT: ["产品对比", "性能报告", "案例研究"],
        OptimizationStrategy.CITATION_OPTIMIZATION: ["研究论文", "白皮书", "深度分析"],
        OptimizationStrategy.STRUCTURAL_OPTIMIZATION: ["长篇文章", "教程指南", "产品说明"],
        OptimizationStrategy.KEYWORD_STRATEGY: ["SEO内容", "产品描述", "营销文案"],
        OptimizationStrategy.MULTIMODAL_ENHANCEMENT: ["产品展示", "教程视频", "数据可视化"]
    }
    return recommendations.get(strategy, [])