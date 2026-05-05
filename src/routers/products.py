"""
AI计算设备产品推广API路由
专门为零刻GTR9 Pro、MINIX T5000、NVIDIA Jetson AGX Thor等产品提供GEO优化内容
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
import uuid

from src.services.product_promotion_generator import (
    ProductPromotionGenerator, 
    ProductPromotionContent,
    ContentType,
    product_promotion_generator
)
from src.services.geo_optimizer import OptimizationStrategy
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

# 请求/响应模型
class ProductPromotionRequest(BaseModel):
    """产品推广请求"""
    product_id: str = Field(..., description="产品ID")
    content_type: str = Field(
        default=ContentType.PRODUCT_DESCRIPTION.value,
        description="内容类型"
    )
    optimization_strategies: List[str] = Field(
        default_factory=lambda: [
            OptimizationStrategy.AUTHORITATIVE_REWRITE.value,
            OptimizationStrategy.STATISTICAL_ENHANCEMENT.value
        ],
        description="优化策略"
    )
    target_platforms: List[str] = Field(
        default_factory=lambda: ["deepseek", "doubao"],
        description="目标平台"
    )
    optimize_in_background: bool = Field(
        default=False, 
        description="是否在后台优化"
    )

class ProductPromotionResponse(BaseModel):
    """产品推广响应"""
    request_id: str = Field(..., description="请求ID")
    product_id: str = Field(..., description="产品ID")
    product_name: str = Field(..., description="产品名称")
    content_type: str = Field(..., description="内容类型")
    title: str = Field(..., description="内容标题")
    content: str = Field(..., description="优化后内容")
    keywords: List[str] = Field(default_factory=list, description="关键词")
    confidence_score: float = Field(..., description="置信度分数")
    optimization_strategies: List[str] = Field(default_factory=list, description="使用的优化策略")
    target_platforms: List[str] = Field(default_factory=list, description="目标平台")
    metadata: dict = Field(default_factory=dict, description="元数据")

class BatchProductPromotionRequest(BaseModel):
    """批量产品推广请求"""
    products: List[dict] = Field(
        ..., 
        description="产品列表，每个元素包含product_id和content_type",
        min_items=1, 
        max_items=10
    )
    optimization_strategies: List[str] = Field(
        default_factory=lambda: [
            OptimizationStrategy.AUTHORITATIVE_REWRITE.value,
            OptimizationStrategy.STATISTICAL_ENHANCEMENT.value
        ],
        description="优化策略"
    )

class BatchProductPromotionResponse(BaseModel):
    """批量产品推广响应"""
    request_id: str = Field(..., description="请求ID")
    status: str = Field(..., description="状态")
    results: List[ProductPromotionResponse] = Field(default_factory=list, description="推广结果")
    total_products: int = Field(..., description="产品总数")
    successful: int = Field(..., description="成功数")
    failed: int = Field(..., description="失败数")

class ProductInfoResponse(BaseModel):
    """产品信息响应"""
    product_id: str = Field(..., description="产品ID")
    name: str = Field(..., description="产品名称")
    category: str = Field(..., description="产品类别")
    description: str = Field(..., description="产品描述")
    pricing: dict = Field(default_factory=dict, description="价格信息")
    specifications: dict = Field(default_factory=dict, description="技术规格")
    ai_capabilities: dict = Field(default_factory=dict, description="AI能力")
    use_cases: dict = Field(default_factory=dict, description="使用场景")
    competitive_advantages: List[str] = Field(default_factory=list, description="竞争优势")
    geo_keywords: List[str] = Field(default_factory=list, description="GEO优化关键词")

class ComparisonRequest(BaseModel):
    """产品对比请求"""
    product_ids: List[str] = Field(
        ..., 
        description="要对比的产品ID列表",
        min_items=2, 
        max_items=5
    )
    comparison_aspects: List[str] = Field(
        default_factory=lambda: ["pricing", "specifications", "ai_capabilities", "use_cases"],
        description="对比方面"
    )

class ComparisonResponse(BaseModel):
    """产品对比响应"""
    request_id: str = Field(..., description="请求ID")
    product_ids: List[str] = Field(..., description="产品ID列表")
    product_names: List[str] = Field(..., description="产品名称列表")
    comparison_content: str = Field(..., description="对比内容")
    summary: dict = Field(default_factory=dict, description="对比总结")

# 推广任务存储
promotion_tasks = {}

@router.get("/", response_model=List[ProductInfoResponse])
async def get_all_products(
    generator: ProductPromotionGenerator = Depends(lambda: product_promotion_generator)
):
    """
    获取所有AI计算设备产品信息
    
    返回系统中所有预配置的AI计算设备产品详细信息
    """
    try:
        products = generator.get_all_products()
        
        response = []
        for product in products:
            response.append(ProductInfoResponse(
                product_id=product.get("id", ""),
                name=product.get("name", ""),
                category=product.get("category", ""),
                description=product.get("description", ""),
                pricing=product.get("pricing", {}),
                specifications=product.get("specifications", {}),
                ai_capabilities=product.get("ai_capabilities", {}),
                use_cases=product.get("use_cases", {}),
                competitive_advantages=product.get("competitive_advantages", []),
                geo_keywords=product.get("geo_optimization_keywords", [])
            ))
        
        return response
        
    except Exception as e:
        logger.error(f"获取产品信息失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取产品信息失败: {str(e)}"
        )

@router.get("/{product_id}", response_model=ProductInfoResponse)
async def get_product_info(
    product_id: str,
    generator: ProductPromotionGenerator = Depends(lambda: product_promotion_generator)
):
    """
    获取特定产品详细信息
    
    根据产品ID获取详细的规格、价格、AI能力等信息
    """
    try:
        product = generator.get_product_by_id(product_id)
        
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"产品 {product_id} 未找到"
            )
        
        return ProductInfoResponse(
            product_id=product.get("id", ""),
            name=product.get("name", ""),
            category=product.get("category", ""),
            description=product.get("description", ""),
            pricing=product.get("pricing", {}),
            specifications=product.get("specifications", {}),
            ai_capabilities=product.get("ai_capabilities", {}),
            use_cases=product.get("use_cases", {}),
            competitive_advantages=product.get("competitive_advantages", []),
            geo_keywords=product.get("geo_optimization_keywords", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取产品 {product_id} 信息失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取产品信息失败: {str(e)}"
        )

@router.post("/promote", response_model=ProductPromotionResponse)
async def promote_product(
    request: ProductPromotionRequest,
    background_tasks: BackgroundTasks,
    generator: ProductPromotionGenerator = Depends(lambda: product_promotion_generator)
):
    """
    生成GEO优化的产品推广内容
    
    为指定AI计算设备生成经过GEO优化的推广内容，提高AI搜索引擎可见性
    """
    request_id = str(uuid.uuid4())
    
    logger.info(f"收到产品推广请求 {request_id}: {request.product_id}")
    
    # 验证产品是否存在
    product = generator.get_product_by_id(request.product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"产品 {request.product_id} 未找到"
        )
    
    if request.optimize_in_background:
        # 后台优化
        background_tasks.add_task(
            _process_promotion_background,
            request_id, request, generator
        )
        
        return ProductPromotionResponse(
            request_id=request_id,
            product_id=request.product_id,
            product_name=product.get("name", "未知产品"),
            content_type=request.content_type,
            title="处理中...",
            content="内容正在后台优化处理中",
            keywords=product.get("geo_optimization_keywords", []),
            confidence_score=0.0,
            optimization_strategies=[],
            target_platforms=request.target_platforms,
            metadata={"status": "processing"}
        )
    else:
        # 同步优化
        return await _process_promotion_sync(request_id, request, generator)

@router.post("/promote/batch", response_model=BatchProductPromotionResponse)
async def batch_promote_products(
    request: BatchProductPromotionRequest,
    generator: ProductPromotionGenerator = Depends(lambda: product_promotion_generator)
):
    """
    批量生成产品推广内容
    
    同时为多个AI计算设备生成GEO优化的推广内容
    """
    request_id = str(uuid.uuid4())
    
    logger.info(f"收到批量产品推广请求 {request_id}: {len(request.products)} 个产品")
    
    import asyncio
    import time
    start_time = time.time()
    
    try:
        # 准备异步任务
        tasks = []
        for product_info in request.products:
            product_id = product_info.get("product_id")
            content_type = product_info.get("content_type", ContentType.PRODUCT_DESCRIPTION.value)
            
            # 验证产品是否存在
            product = generator.get_product_by_id(product_id)
            if not product:
                logger.warning(f"产品 {product_id} 未找到，跳过")
                continue
            
            # 创建推广请求
            promotion_request = ProductPromotionRequest(
                product_id=product_id,
                content_type=content_type,
                optimization_strategies=request.optimization_strategies,
                target_platforms=["deepseek", "doubao"],
                optimize_in_background=False
            )
            
            # 添加到任务列表
            task_id = str(uuid.uuid4())
            task = _process_promotion_sync(task_id, promotion_request, generator)
            tasks.append(task)
        
        # 并发执行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 处理结果
        promotion_responses = []
        successful = 0
        failed = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"产品推广失败: {str(result)}")
                failed += 1
            else:
                promotion_responses.append(result)
                successful += 1
        
        return BatchProductPromotionResponse(
            request_id=request_id,
            status="completed",
            results=promotion_responses,
            total_products=len(request.products),
            successful=successful,
            failed=failed
        )
        
    except Exception as e:
        logger.error(f"批量产品推广失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"批量产品推广失败: {str(e)}"
        )

@router.post("/compare", response_model=ComparisonResponse)
async def compare_products(
    request: ComparisonRequest,
    generator: ProductPromotionGenerator = Depends(lambda: product_promotion_generator)
):
    """
    对比多个AI计算设备
    
    生成详细的产品对比分析，帮助用户选择最适合的设备
    """
    request_id = str(uuid.uuid4())
    
    logger.info(f"收到产品对比请求 {request_id}: {request.product_ids}")
    
    try:
        # 验证所有产品是否存在
        products = []
        product_names = []
        
        for product_id in request.product_ids:
            product = generator.get_product_by_id(product_id)
            if not product:
                raise HTTPException(
                    status_code=404,
                    detail=f"产品 {product_id} 未找到"
                )
            products.append(product)
            product_names.append(product.get("name", "未知产品"))
        
        # 生成对比内容
        comparison_content = generator.generate_comparison_article(
            product_ids=request.product_ids,
            comparison_aspects=request.comparison_aspects
        )
        
        # 生成对比总结
        summary = generator.products_data.get("comparison_summary", {})
        best_for = summary.get("best_for", {})
        
        comparison_summary = {}
        for product in products:
            product_id = product.get("id", "")
            comparison_summary[product_id] = {
                "name": product.get("name", ""),
                "best_for": best_for.get(product_id, "多种场景"),
                "price_range": product.get("pricing", {}).get("price_range", "待定")
            }
        
        return ComparisonResponse(
            request_id=request_id,
            product_ids=request.product_ids,
            product_names=product_names,
            comparison_content=comparison_content,
            summary=comparison_summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"产品对比失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"产品对比失败: {str(e)}"
        )

@router.get("/content-types")
async def get_content_types():
    """
    获取可用的内容类型
    
    返回系统支持的所有产品推广内容类型
    """
    content_types = [
        {
            "id": ContentType.PRODUCT_DESCRIPTION.value,
            "name": "产品描述",
            "description": "详细的产品介绍和规格说明",
            "recommended_for": ["新产品推广", "技术规格介绍"]
        },
        {
            "id": ContentType.COMPARISON_ARTICLE.value,
            "name": "对比文章", 
            "description": "多个产品的详细对比分析",
            "recommended_for": ["购买决策", "竞品分析"]
        },
        {
            "id": ContentType.USE_CASE_SCENARIO.value,
            "name": "使用场景",
            "description": "具体应用场景和解决方案",
            "recommended_for": ["解决方案销售", "案例展示"]
        },
        {
            "id": ContentType.TECHNICAL_REVIEW.value,
            "name": "技术评测",
            "description": "技术深度分析和性能评测",
            "recommended_for": ["技术用户", "性能评估"]
        },
        {
            "id": ContentType.BUYING_GUIDE.value,
            "name": "购买指南",
            "description": "购买建议和配置推荐",
            "recommended_for": ["销售支持", "客户咨询"]
        }
    ]
    
    return {
        "content_types": content_types,
        "count": len(content_types)
    }

@router.get("/task/{task_id}")
async def get_promotion_task_status(task_id: str):
    """
    获取推广任务状态
    
    查询后台产品推广任务的状态和结果
    """
    if task_id not in promotion_tasks:
        raise HTTPException(
            status_code=404,
            detail=f"推广任务 {task_id} 不存在"
        )
    
    task_info = promotion_tasks[task_id]
    
    return {
        "task_id": task_id,
        "status": task_info.get("status", "unknown"),
        "product_id": task_info.get("product_id"),
        "content_type": task_info.get("content_type"),
        "created_at": task_info.get("created_at"),
        "updated_at": task_info.get("updated_at"),
        "result": task_info.get("result"),
        "error": task_info.get("error")
    }

# 辅助函数
async def _process_promotion_sync(
    request_id: str,
    request: ProductPromotionRequest,
    generator: ProductPromotionGenerator
) -> ProductPromotionResponse:
    """同步处理产品推广"""
    import time
    start_time = time.time()
    
    try:
        # 生成GEO优化内容
        result = await generator.generate_geo_optimized_content(
            product_id=request.product_id,
            content_type=request.content_type,
            optimization_strategies=request.optimization_strategies,
            target_platforms=request.target_platforms
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 获取产品信息
        product = generator.get_product_by_id(request.product_id)
        
        return ProductPromotionResponse(
            request_id=request_id,
            product_id=result.product_id,
            product_name=product.get("name", "未知产品") if product else "未知产品",
            content_type=result.content_type,
            title=result.title,
            content=result.content,
            keywords=result.keywords,
            confidence_score=result.metadata.get("geo_optimization", {}).get("confidence_score", 0.0),
            optimization_strategies=result.optimization_strategies,
            target_platforms=result.target_platforms,
            metadata={
                "processing_time": processing_time,
                "content_length": len(result.content),
                "product_info": result.metadata.get("product_info", {}),
                "geo_optimization": result.metadata.get("geo_optimization", {}),
                "structured_data": result.metadata.get("structured_data", {})
            }
        )
        
    except Exception as e:
        logger.error(f"产品推广失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"产品推广失败: {str(e)}"
        )

async def _process_promotion_background(
    request_id: str,
    request: ProductPromotionRequest,
    generator: ProductPromotionGenerator
):
    """后台处理产品推广"""
    import time
    from datetime import datetime
    
    task_info = {
        "request_id": request_id,
        "product_id": request.product_id,
        "content_type": request.content_type,
        "status": "processing",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "result": None,
        "error": None
    }
    
    promotion_tasks[request_id] = task_info
    
    try:
        start_time = time.time()
        
        # 生成GEO优化内容
        result = await generator.generate_geo_optimized_content(
            product_id=request.product_id,
            content_type=request.content_type,
            optimization_strategies=request.optimization_strategies,
            target_platforms=request.target_platforms
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 获取产品信息
        product = generator.get_product_by_id(request.product_id)
        
        task_info["status"] = "completed"
        task_info["updated_at"] = datetime.now().isoformat()
        task_info["result"] = {
            "product_name": product.get("name", "未知产品") if product else "未知产品",
            "title": result.title,
            "content_length": len(result.content),
            "confidence_score": result.metadata.get("geo_optimization", {}).get("confidence_score", 0.0),
            "processing_time": processing_time,
            "keywords": result.keywords[:10]  # 只存储前10个关键词
        }
        
        logger.info(f"后台产品推广任务 {request_id} 完成: {request.product_id}")
        
    except Exception as e:
        task_info["status"] = "failed"
        task_info["updated_at"] = datetime.now().isoformat()
        task_info["error"] = str(e)
        
        logger.error(f"后台产品推广任务 {request_id} 失败: {str(e)}")