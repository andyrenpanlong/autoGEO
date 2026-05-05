"""
GEO Promotion Backend 使用示例
"""

import asyncio
import json
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

async def example_optimize_content():
    """示例：优化内容"""
    from src.services.geo_optimizer import GEOOptimizer, OptimizationStrategy
    
    print("=== 示例1: 优化产品推广内容 ===\n")
    
    # 创建优化器
    optimizer = GEOOptimizer()
    
    # 产品信息
    product_info = {
        "name": "智能AI写作助手",
        "description": "一款基于大语言模型的智能写作工具",
        "category": "AI工具",
        "features": [
            "智能内容生成",
            "多语言支持", 
            "SEO优化建议",
            "实时语法检查"
        ],
        "keywords": ["AI写作", "智能助手", "内容生成", "SEO优化"],
        "statistics": {
            "user_satisfaction": "95%",
            "time_saved": "70%",
            "content_quality_improvement": "40%"
        },
        "target_audience": "内容创作者、营销人员、企业",
        "brand": "TechAI"
    }
    
    # 原始内容
    original_content = """
    我们的AI写作助手可以帮助您快速生成高质量的内容。
    它支持多种写作场景，包括博客文章、营销文案、产品描述等。
    使用先进的大语言模型技术，确保内容自然流畅。
    """
    
    print(f"原始内容:\n{original_content}\n")
    
    # 优化策略
    strategies = [
        OptimizationStrategy.AUTHORITATIVE_REWRITE,
        OptimizationStrategy.STATISTICAL_ENHANCEMENT,
        OptimizationStrategy.STRUCTURAL_OPTIMIZATION
    ]
    
    # 执行优化
    result = await optimizer.optimize_content(
        content=original_content,
        product_info=product_info,
        target_platforms=["deepseek", "doubao"],
        strategies=strategies
    )
    
    print(f"优化后内容:\n{result.optimized_content}\n")
    print(f"使用的策略: {result.strategy_used}")
    print(f"置信度分数: {result.confidence_score:.2f}")
    print(f"结构化数据: {json.dumps(result.metadata.get('structured_data', {}), indent=2, ensure_ascii=False)}")
    
    return result

async def example_batch_optimize():
    """示例：批量优化"""
    from src.services.geo_optimizer import GEOOptimizer
    
    print("\n=== 示例2: 批量优化内容 ===\n")
    
    optimizer = GEOOptimizer()
    
    # 产品信息
    product_info = {
        "name": "云端项目管理工具",
        "description": "基于云的团队协作和项目管理平台",
        "category": "SaaS工具",
        "features": ["任务管理", "团队协作", "进度跟踪", "文档共享"],
        "keywords": ["项目管理", "团队协作", "SaaS", "云端工具"]
    }
    
    # 多个内容
    contents = [
        "我们的项目管理工具提供直观的任务看板，帮助团队跟踪进度。",
        "实时协作功能让团队成员可以同时编辑文档和讨论任务。",
        "强大的报告和分析功能帮助管理者了解项目状态和团队效率。"
    ]
    
    print(f"批量优化 {len(contents)} 个内容...\n")
    
    # 批量优化
    results = await optimizer.batch_optimize(
        contents=contents,
        product_info=product_info,
        target_platforms=["general"]
    )
    
    for i, result in enumerate(results):
        print(f"内容 {i+1} 优化结果:")
        print(f"  原始长度: {len(result.original_content)} 字符")
        print(f"  优化后长度: {len(result.optimized_content)} 字符")
        print(f"  置信度: {result.confidence_score:.2f}")
        print(f"  策略: {result.strategy_used}")
        print()
    
    return results

async def example_distribute_content():
    """示例：分发内容"""
    from src.services.distribution_service import distribution_service
    
    print("\n=== 示例3: 分发内容到AI平台 ===\n")
    
    # 初始化分发服务
    await distribution_service.initialize()
    
    # 获取平台状态
    platform_status = await distribution_service.get_platform_status()
    print(f"可用平台: {list(platform_status.keys())}\n")
    
    # 要分发的内容
    content = """
    智能AI写作助手是一款革命性的内容创作工具，基于最新的大语言模型技术开发。
    它能够帮助用户快速生成高质量的文章、营销文案、产品描述等内容。
    经过测试，使用该工具可以平均节省70%的写作时间，同时提高内容质量40%。
    该工具特别适合内容创作者、营销人员和企业使用。
    """
    
    metadata = {
        "content_id": "ai_writing_tool_001",
        "product_name": "智能AI写作助手",
        "category": "AI工具",
        "keywords": ["AI写作", "内容生成", "效率工具"],
        "target_audience": "内容创作者、营销人员"
    }
    
    # 分发到可用平台
    platforms = ["deepseek", "doubao"]  # 示例平台
    
    print(f"分发内容到平台: {platforms}\n")
    
    results = await distribution_service.distribute_to_platforms(
        content=content,
        metadata=metadata,
        platform_names=platforms
    )
    
    for result in results:
        status = "成功" if result.success else "失败"
        print(f"平台 {result.platform}: {status}")
        if result.error_message:
            print(f"  错误: {result.error_message}")
        print(f"  内容ID: {result.content_id}")
        print()
    
    return results

async def example_monitor_performance():
    """示例：监控性能"""
    from src.services.monitoring_service import monitoring_service
    
    print("\n=== 示例4: 监控内容性能 ===\n")
    
    # 测试内容
    content_id = "test_content_001"
    content = "这是一个测试内容，用于演示监控功能。"
    
    print(f"监控内容: {content_id}\n")
    
    # 检查引用情况
    citation_metrics = await monitoring_service.check_citations(
        content_id=content_id,
        content=content,
        platforms=["openai", "deepseek", "perplexity"]
    )
    
    for metrics in citation_metrics:
        print(f"平台 {metrics.platform}:")
        print(f"  引用数: {metrics.citation_count}")
        print(f"  置信度: {metrics.citation_confidence:.2f}")
        print(f"  查询示例: {metrics.query_examples[:2]}")
        print()
    
    # 获取性能指标
    performance = await monitoring_service.get_content_performance(content_id)
    
    if performance:
        print(f"内容性能指标:")
        print(f"  总引用数: {performance.total_citations}")
        print(f"  平台分布: {performance.platform_citations}")
        print(f"  性能分数: {performance.performance_score:.1f}/100")
        print()
    
    return citation_metrics

async def example_competitor_analysis():
    """示例：竞品分析"""
    from src.services.monitoring_service import monitoring_service
    
    print("\n=== 示例5: 竞品分析 ===\n")
    
    product_name = "智能AI写作助手"
    competitors = ["竞品A", "竞品B", "竞品C"]
    
    print(f"分析产品: {product_name}")
    print(f"竞品: {competitors}\n")
    
    analyses = await monitoring_service.analyze_competitors(
        product_name=product_name,
        competitor_names=competitors
    )
    
    for analysis in analyses:
        print(f"竞品: {analysis.competitor_name}")
        print(f"  估计AI引用数: {analysis.citation_count}")
        print(f"  内容数量: {analysis.content_volume}")
        print(f"  优化策略: {analysis.optimization_strategies}")
        print(f"  优势: {analysis.strengths[:2]}")
        print(f"  劣势: {analysis.weaknesses[:2]}")
        print(f"  建议: {analysis.recommendation}")
        print()
    
    return analyses

async def main():
    """主函数"""
    print("GEO Promotion Backend 使用示例")
    print("=" * 50)
    
    try:
        # 运行所有示例
        await example_optimize_content()
        await example_batch_optimize()
        await example_distribute_content()
        await example_monitor_performance()
        await example_competitor_analysis()
        
        print("=" * 50)
        print("所有示例执行完成！")
        
    except Exception as e:
        print(f"示例执行失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())